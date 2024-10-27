import boto3
import os
from pyspark.sql import SparkSession,Row
from pyspark.sql.types import StructType,StructField,StringType,IntegerType,FloatType,ArrayType,IntegerType,LongType
from difflib import SequenceMatcher
from pyspark.sql.functions import udf,regexp_replace

MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_HOST = os.environ.get('MINIO_HOST')

BRONZE_BUCKET = 'bronze'
SILVER_BUCKET = 'silver'

city_mapping = {}

def handle_price_string(string_test,price):
    string_test = string_test.strip().lower().replace("\xa0","")
    if string_test.find("/m2") != -1:
        return string_test.replace(" vnđ","")
    elif string_test == 'thương lượng' or string_test == 'liên hệ' or string_test=='giá thỏa thuận' or string_test == 'thỏa thuận':
        string_test = 'Thỏa thuận'
        return string_test
    else:
        amount_list = ["đồng","nghìn","triệu","tỷ"]
        price_str =''
        for t in range(0, 4):
            temp = price%1000
            price = price//1000
            if temp == 0:
                continue
            else:
                price_str = ' '+str(int(temp))+' '+ amount_list[t] + price_str
            if amount_list[t] == 'tỷ' and price%1000 != 0: 
                t =0
        return price_str[1:]

def handle_property_type(test_type):
    apartment_type=['Apartment','Penthouse','Chung cư','Chung cư mini','Condotel','Căn hộ','Căn hộ chung cư','Căn hộ dịch vụ - Homestay','Căn hộ dịch vụ, mini', 
                    'Căn hộ khách sạn - Condotel','Căn hộ/Chung cư','Tập thể, cư xá', 'căn hộ - chung cư', 'căn hộ Condotel', 'căn hộ chung cư', 'Căn hộ khách sạn - Condotel',
                    'Căn hộ/Chung cư','Căn hộ','Căn hộ chung cư','Căn hộ dịch vụ - Homestay','Căn hộ dịch vụ, mini', 'Nhà Chung Cư']
    house_type=['Biệt thự''Biệt thự, Villa','Biệt thự, Villa, Penthouse','Biệt thự, liền kề','Biệt thự, liền kề, phân lô', 'House', 'Khu nghỉ dưỡng - Resort',
                'Nhà Biệt Thự, Dự Án', 'Nhà Mặt Tiền','Nhà Riêng', 'Nhà biệt thự, liền kề', 'Nhà cấp 4','Nhà hẻm, ngõ','Nhà mặt phố', 'Nhà mặt tiền',
                'Nhà mặt tiền, phố', 'Nhà ngõ, hẻm', 'Nhà phố','Nhà riêng', 'Nhà trong ngõ', 'Nhà tập thể','Nhà ở', 'biệt thự', 'biệt thự, nhà liền kề',
                'nhà mặt phố', 'nhà mặt tiền','nhà riêng', 'nhà riêng, nhà mặt phố','Liền kề']
    shop_type=['Cây xăng', 'Karaoke, bar', 'Kho Nhà Xưởng','Kho bãi - Nhà xưởng - Khu công nghiệp','Kho bãi, nhà xưởng','Kho, xưởng','Khu tiện ích dự án, Khu vui chơi giải trí',
               'Hoa viên nghĩa trang','Khách sạn - Nhà nghỉ','Matxa-Spa', 'Nhà hàng - Cửa hàng - Ki ốt','Nhà hàng, khách sạn', 'Nhà phố thương mại - Shophouse', 'Nhà phố thương mại Shophouse',
               'Nhà xưởng', 'Officetel','Căn hộ văn phòng - Officetel','Phòng học','Phòng họp, hội nghị','Phòng trọ','Phòng trọ, nhà trọ', 'Quán cafe', 'Shop', 'Shop, kiot, quán','ShopHouse',
               'Sân bãi - Điểm đỗ xe','Sân bóng, sân tennis, Thể thao', 'Trung tâm chăm sóc xe, bãi rửa xe','Trường học', 'Trường mầm non','Tòa nhà văn phòng','Văn phòng', 'Văn phòng Co-working',
               'Văn phòng, Mặt bằng kinh doanh', 'Vị trí đặt biển bảng quảng cáo', 'Xưởng sản xuất thực phẩm', 'căn hộ officetel','cửa hàng, kiot, shophouse', 'kho - nhà xưởng', 'kho, nhà xưởng, kiot',
               'kho, xưởng', 'nhà hàng, khách sạn', 'nhà trọ', 'toà nhà văn phòng','Căn hộ văn phòng - Officetel']
    land_type=[ 'Land','Mặt bằng','Mặt bằng, cửa hàng', 'Trang trại','Trang trại, khu nghỉ dưỡng', 'trang trại', 'Đất','Đất Biệt Thự, Dự Án','Đất Mặt Tiền','Đất Riêng',
               'Đất Trang Trại','Đất dự án, Khu dân cư','Đất nông nghiệp, kho bãi', 'Đất nông, lâm nghiệp', 'Đất nền dự án','Đất nền, phân lô','Đất thổ cư','Đất, nền dự án',
               'đất', 'đất nền', 'đất nền dự án','đất thổ cư','đất trang trại, nghỉ dưỡng']
    other_type=['Bất động sản khác','Cho thuê căn hộ','Cho thuê kho, nhà xưởng','Cho thuê mặt bằng','Cho thuê nhà mặt tiền' 'Cho thuê phòng trọ', 'Cho thuê đất',
                'Chung Cư Thuê','Các loại khác','Căn hộ cho thuê', 'Dự án BĐS', 'Nhà trọ', 'Nhà Đất Khác', 'Thuê Nhà Riêng','Thuê Văn Phòng', 'Thuê nhà nguyên căn',
                'bất động sản khác','nhà đất khác', 'Mua bán nhà đất']
    if test_type in apartment_type:
        return 'apartment'
    elif test_type in house_type:
        return 'house'
    elif test_type in shop_type:
        return 'shop'
    elif test_type in land_type:
        return 'land'
    else:
        return 'orther'

def handle_location(location):
    global city_mapping
    city = location.city
    city_list = ['Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Bình Dương', 'An Giang', 'Bà Rịa Vũng Tàu', 
             'Bạc Liêu', 'Bắc Giang', 'Bắc Kạn', 'Bắc Ninh', 'Bến Tre', 'Bình Định', 'Bình Phước', 'Bình Thuận', 
             'Cà Mau', 'Cao Bằng', 'Cần Thơ', 'Đắk Lắk', 'Đắk Nông', 'Điện Biên', 'Đồng Nai', 'Đồng Tháp', 
             'Gia Lai', 'Hà Giang', 'Hà Nam', 'Hà Tĩnh', 'Hải Dương', 'Hải Phòng', 'Hậu Giang', 'Hòa Bình', 
             'Hưng Yên', 'Kiên Giang', 'Kon Tum', 'Khánh Hòa', 'Lai Châu', 'Lạng Sơn', 'Lào Cai', 'Lâm Đồng', 'Long An', 
             'Nam Định', 'Ninh Bình', 'Ninh Thuận', 'Nghệ An', 'Phú Thọ', 'Phú Yên', 'Quảng Bình', 'Quảng Nam', 'Quảng Ninh',
             'Quảng Ngãi', 'Quảng Trị', 'Sóc Trăng', 'Sơn La', 'Tây Ninh', 'Tiền Giang', 'Tuyên Quang', 'Thái Bình',
             'Thái Nguyên', 'Thanh Hóa', 'Thừa Thiên Huế', 'Trà Vinh', 'Vĩnh Long', 'Vĩnh Phúc', 'Yên Bái']

    max_ratio = 0
    city_similar = ''
    if city in city_mapping:
        city_similar = city_mapping[city]
    else:
        for city1 in city_list:
            similarity_ratio = SequenceMatcher(None,city, city1).ratio()
            if similarity_ratio >0.8:
                max_ratio = similarity_ratio
                city_similar = city1
                break
            if max_ratio < similarity_ratio :
                max_ratio = similarity_ratio
                city_similar = city1
        if city_similar not in ['Hà Nội','Hồ Chí Minh','Đà Nẵng','Cần Thơ','Hải Phòng']:
            city_similar = 'Tỉnh ' +city_similar
        else:
            city_similar = 'Thành phố ' +city_similar
        city_mapping[city]= city_similar
    
    dist = location.dist
    ward = location.ward
    street= location.street
    address = location.address
    dist = dist.strip()
    
    if dist.find("Tp.") != -1:
        dist=dist.replace("Tp.","")
        address = address.replace("Tp.","")
    elif dist.find("TP.") != -1:    
        dist=dist.replace("TP.","")
        address = address.replace("TP.","")
    elif dist.find("Tx.") != -1:
        dist=dist.replace("Tx.","Thị xã ")
        address = address.replace("Tx.","Thị xã")
    elif dist.find("Q.") != -1:
        dist=dist.replace("Q.","Quận ")
        address = address.replace("Q.","Quận ")
    elif dist.find("H.") != -1:
        dist=dist.replace("H.","Huyện ")
        address = address.replace("H.","Huyện ")
    elif dist.find(".") != -1:
        dist = dist.replace(".","")
    
    if ward is not None:
        ward = ward.strip()   
        if ward.find("P.") != -1: 
            ward=ward.replace("P.","Phường ")
            address = address.replace("P.","Phường ")
        elif ward.find("X.") != -1:
            ward=ward.replace("X.","Xã ")
            address = address.replace("X.","Xã ")
        elif ward.find(".") != -1:
            ward = ward.replace(".","")    
    
    if street is not None:
        street = street.strip()
        if street.find("Đ.") != -1:
            street = street.replace("Đ.","Đường ")
            address = address.replace("Đ.","Đường ")
        elif street.find("đ.")!= -1:
            street = street.replace("đ.","Đường ")
            address = address.replace("đ.","Đường ")
        elif street.find(".") != -1:
            street = street.replace(".","")
            
    if address is not None :    
        address = address.strip()
        if address.find("đ.")!= -1:
            address = address.replace("đ.","Đường ")
        if address.find(".")!= -1:
            address = address.replace(".","")

    updated_location =Row(
        address = address,
        city = city_similar,
        description = location.description,
        dist = dist,
        lat = location.lat,
        long =location.long,
        street = street,
        ward =ward
    ) 
    return updated_location


def transform_data(spark_df):
    
    spark_df = spark_df.filter(~(spark_df['price_string'].rlike("Triệu/Tháng")))
    spark_df = spark_df.filter(~(spark_df['price_string'].rlike("Tỷ/Tháng")))
    spark_df = spark_df.filter(~(spark_df['price_string'].rlike("ngàn")))
    
    transform_price_string = udf(handle_price_string,StringType())
    spark_df =  spark_df.withColumn("price_string",transform_price_string(spark_df["price_string"],spark_df["price"]))
    
    transform_property_type = udf(handle_property_type,StringType())
    spark_df = spark_df.withColumn("property_type",transform_property_type(spark_df["property_type"]))
    
    
    schema =StructType([
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("description", StringType(), True),
        StructField("dist", StringType(), True),
        StructField("lat", FloatType(), True),
        StructField("long", FloatType(), True),
        StructField("street", StringType(), True),
        StructField("ward", StringType(), True),
    ])
    transform_location = udf(handle_location,schema)
    spark_df = spark_df.withColumn("location",transform_location(spark_df["location"]))
    
    
    spark_df = spark_df.withColumn("description",regexp_replace("description","\\u200d|<[^>]+>|&#[0-9]+;|\\n|\\r|-|>>|\\xa0|[0-9]+\*+|Đã sao chép|Hiện số|Xem thêm|click để xem","."))
    

    print('Data transformed sucessfully')
    return spark_df

def create_Schema():
    schema = StructType([
        StructField("_id", StringType(), True),
        StructField("url", StringType(), True),
        StructField("agent", StructType([
            StructField("address", StringType(), True),
            StructField("agent_type", StringType(), True),
            StructField("email", StringType(), True),
            StructField("name", StringType(), True),
            StructField("phone_number", StringType(), True),
            StructField("profile", StringType(), True),
        ]), True),
        StructField("attr", StructType([
            StructField("area", FloatType(), True),
            StructField("bathroom", IntegerType(), True),
            StructField("bedroom", IntegerType(), True),
            StructField("built_year", IntegerType(), True),
            StructField("certificate", StringType(), True),
            StructField("condition", StringType(), True),
            StructField("direction", StringType(), True),
            StructField("feature", StringType(), True),
            StructField("floor", FloatType(), True),
            StructField("floor_num", FloatType(), True),
            StructField("height", FloatType(), True),
            StructField("interior", StringType(), True),
            StructField("length", FloatType(), True),
            StructField("site_id", StringType(), True),
            StructField("total_area", FloatType(), True),
            StructField("total_room", IntegerType(), True),
            StructField("type_detail", StringType(), True),
            StructField("width", FloatType(), True),
        ]), True),
        StructField("description", StringType(), True),
        StructField("id", StringType(), True),
        StructField("images", ArrayType(StringType(), True), True),
        StructField("initial_at", StringType(), True),
        StructField("location", StructType([
            StructField("address", StringType(), True),
            StructField("city", StringType(), True),
            StructField("description", StringType(), True),
            StructField("dist", StringType(), True),
            StructField("lat", FloatType(), True),
            StructField("long", FloatType(), True),
            StructField("street", StringType(), True),
            StructField("ward", StringType(), True),
        ]), True),
        StructField("price", LongType(), True),
        StructField("price_currency", StringType(), True),
        StructField("price_string", StringType(), True),
        StructField("project", StructType([
            StructField("name", StringType(), True),
            StructField("profile", StringType(), True),
        ]), True),
        StructField("property_type", StringType(), True),
        StructField("publish_at", StringType(), True),
        StructField("site", StringType(), True),
        StructField("thumbnail", StringType(), True),
        StructField("title", StringType(), True),
        StructField("update_at", StringType(), True),
        StructField("initial_date", StringType(), True)
    ])
    return schema

def create_spark_connection():
    s_conn = None
    try:
        s_conn = SparkSession.builder \
                .appName("MinIOExtractFile") \
                .config("fs.s3a.endpoint", MINIO_HOST)\
                .config("fs.s3a.access.key", MINIO_ACCESS_KEY)\
                .config("fs.s3a.secret.key", MINIO_SECRET_KEY )\
                .config("spark.hadoop.fs.s3a.path.style.access", "true")\
                .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.2.2")\
                .config("spark.hadoop.fs.s3a.impl","org.apache.hadoop.fs.s3a.S3AFileSystem")\
                .config('spark.hadoop.fs.s3a.aws.credentials.provider', 'org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider')\
                .config("spark.sql.parquet.enableVectorizedReader","false")\
                .config("spark.sql.parquet.writeLegacyFormat","true")\
                .getOrCreate()

        s_conn.sparkContext.setLogLevel("ERROR")
        s_conn.conf.set("mapreduce.fileoutputcommitter.marksuccessfuljobs", "false")
        print("Spark connection created successfully!")
    except Exception as e:
        print(f"Couldn't create the spark session due to exception {e}")

    return s_conn

def create_s3_connection():
    try:
        s3 = boto3.client(
            's3',
            endpoint_url = MINIO_HOST,
            aws_access_key_id = MINIO_ACCESS_KEY,
            aws_secret_access_key = MINIO_SECRET_KEY,
            region_name='us-east-1'
        )
    except:
        raise Exception("Can't connect to minIO")
    
    #checking bronze bucket is exist or not
    try:
        s3.head_bucket(Bucket=BRONZE_BUCKET)
    except:
        raise Exception("Bronze bucket not exist")
    
    try:
        s3.head_bucket(Bucket=SILVER_BUCKET)
    except:
        s3.create_bucket(Bucket=SILVER_BUCKET)
        
    print("S3 connection created successfully!")
    return s3

def get_folder_not_in_silver():
    bronze_response = s3.list_objects_v2(Bucket=BRONZE_BUCKET, Prefix='', Delimiter='/')
    bronze_folder_names =set(prefix.get('Prefix') for prefix in bronze_response.get('CommonPrefixes', []))
    
    silver_respose = s3.list_objects_v2(Bucket=SILVER_BUCKET, Prefix='', Delimiter='/')
    silver_folder_names =set(prefix.get('Prefix') for prefix in silver_respose.get('CommonPrefixes', []))
    
    return list(bronze_folder_names - silver_folder_names)

def connect_to_minIO(spark_conn,folder_name):
    spark_df = None
    s3_path = f"s3a://{BRONZE_BUCKET}/{folder_name}"
    try:
        schema = create_Schema()
        spark_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_path)
        print(f"MinIO data extracted folder {folder_name} successfully")
    except Exception as e:
        print(f"MinIO dataframe could not be created because: {e}")
    
    return spark_df

        

# log4jLogger = spark.sparkContext._jvm.org.apache.log4j
# LOGGER = log4jLogger.LogManager.getLogger(__name__)


if __name__ == "__main__":
    # create spark connection                                                                                                                                                                                                                                        
    spark_conn = create_spark_connection()
    s3 = create_s3_connection()
    print("Processing start .....")
    if spark_conn is not None:
        folder_names = get_folder_not_in_silver()
        for folder in folder_names:
            spark_df = connect_to_minIO(spark_conn,folder)
            transformed_df = transform_data(spark_df)
            #streaming
            try:
                s3_dest=f"s3a://{SILVER_BUCKET}/{folder}"
                streaming_query = transformed_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(s3_dest)
                print(f"Data loaded to {folder} successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
                
    print("Processing end .....")
    spark_conn.stop()

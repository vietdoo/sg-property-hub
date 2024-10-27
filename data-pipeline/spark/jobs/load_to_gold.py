import boto3
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,StringType,IntegerType,FloatType,ArrayType,IntegerType,LongType
from pyspark.sql.functions import udf

MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_HOST = os.environ.get('MINIO_HOST')

SILVER_BUCKET = 'silver'
GOLD_BUCKET = 'gold'

def convert_images_to_string(list_img):
    if list_img is not None:
        img_string ='['
        for img in list_img:
            img_string=img_string + img+','
        if len(img_string) > 1:
            img_string= img_string[:-1]+']'
        return img_string
    else:
        return None

def flat_dataframe(spark_df):
    nested_struct_name = ['agent','attr','location','project']
    df_flattened = spark_df
    for nest in nested_struct_name:
        for sub in schema[f"{nest}"].dataType.fields:
            df_flattened = df_flattened.withColumn(f"{nest}_{sub.name}", spark_df[f"{nest}.{sub.name}"])
        df_flattened = df_flattened.drop(nest)
    
    convert_to_string = udf(convert_images_to_string,StringType())
    df_flattened = df_flattened.withColumn("image", convert_to_string(spark_df["images"]))
    df_flattened = df_flattened.drop('images')    
    return df_flattened

def create_house_parquet(spark_df):
    house_df = spark_df.drop('agent','attr','location','project')
    return house_df

def create_location_parquet(spark_df):
    house_df = spark_df.select("id","location")
    for sub in schema["location"].dataType.fields:
        house_df = house_df.withColumn(f"{sub.name}", spark_df[f"location.{sub.name}"])
    house_df = house_df.drop("location")
    return house_df

def create_attr_parquet(spark_df):
    attr_df = spark_df.select("id","attr")
    for sub in schema["attr"].dataType.fields:
        attr_df = attr_df.withColumn(f"{sub.name}", spark_df[f"attr.{sub.name}"])
    attr_df = attr_df.drop("attr")
    return attr_df

def create_agent_parquet(spark_df):
    agent_df = spark_df.select("id","agent")
    for sub in schema["agent"].dataType.fields:
        agent_df = agent_df.withColumn(f"{sub.name}", spark_df[f"agent.{sub.name}"])
    agent_df = agent_df.drop("agent")
    return agent_df

def create_project_parquet(spark_df):
    project_df = spark_df.select("id","project")
    for sub in schema["project"].dataType.fields:
        project_df = project_df.withColumn(f"{sub.name}", spark_df[f"project.{sub.name}"])
    project_df = project_df.drop("project")
    return project_df

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
        s3.head_bucket(Bucket=SILVER_BUCKET)
    except:
        raise Exception("Silver bucket not exist")
    
    try:
        s3.head_bucket(Bucket=GOLD_BUCKET)
    except:
        s3.create_bucket(Bucket=GOLD_BUCKET)
        
    print("S3 connection created successfully!")
    return s3

def get_folder_not_in_gold():
    silver_response = s3.list_objects_v2(Bucket=SILVER_BUCKET, Prefix='', Delimiter='/')
    silver_folder_names =set(prefix.get('Prefix') for prefix in silver_response.get('CommonPrefixes', []))
    
    gold_respose = s3.list_objects_v2(Bucket=GOLD_BUCKET, Prefix='', Delimiter='/')
    gold_folder_names =set(prefix.get('Prefix') for prefix in gold_respose.get('CommonPrefixes', []))
    
    return list(silver_folder_names - gold_folder_names)

def connect_to_minIO(spark_conn,folder_name):
    spark_df = None
    s3_path = f"s3a://{SILVER_BUCKET}/{folder_name}"
    try:
        schema = create_Schema()
        spark_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_path)
        print("MinIO data extracted successfully")
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
        schema = create_Schema()
        folder_names = get_folder_not_in_gold()
        for folder in folder_names:
                
            spark_df = connect_to_minIO(spark_conn,folder)
            spark_df = spark_df.drop("_id")
           
            #streaming
            df_flattened = flat_dataframe(spark_df)
            try:
                flat_dest=f"s3a://{GOLD_BUCKET}/{folder}/flat"
                streaming_query = df_flattened.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(flat_dest)
                print(f"Data loaded to {folder}/flat successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
            
            house_df = create_house_parquet(spark_df)
            try:
                house_dest=f"s3a://{GOLD_BUCKET}/{folder}/house"
                streaming_query = house_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(house_dest)
                print(f"Data loaded to {folder}/house successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
            
            location_df = create_location_parquet(spark_df)
            try:
                location_dest=f"s3a://{GOLD_BUCKET}/{folder}/location"
                streaming_query = location_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(location_dest)
                print(f"Data loaded to {folder}/location successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
                
            attr_df = create_attr_parquet(spark_df)
            try:
                attr_dest=f"s3a://{GOLD_BUCKET}/{folder}/attr"
                streaming_query = attr_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(attr_dest)
                print(f"Data loaded to {folder}/attr successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
                
            project_df = create_project_parquet(spark_df)
            try:
                project_dest=f"s3a://{GOLD_BUCKET}/{folder}/project"
                streaming_query = project_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(project_dest)
                print(f"Data loaded to {folder}/project successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")
                
            agent_df = create_agent_parquet(spark_df)
            try:
                agent_dest=f"s3a://{GOLD_BUCKET}/{folder}/agent"
                streaming_query = agent_df.coalesce(1).write \
                    .mode("overwrite")\
                    .parquet(agent_dest)
                print(f"Data loaded to {folder}/agent successfully")
            except Exception as e:
                print(f"Data could not be loaded because: {e}")


                
    print("Processing end .....")
    spark_conn.stop()

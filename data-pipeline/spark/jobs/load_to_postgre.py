import boto3
import psycopg2
import os
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,StringType,IntegerType,FloatType,IntegerType,LongType

MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_HOST = os.environ.get('MINIO_HOST')


SILVER_BUCKET = 'silver'
GOLD_BUCKET = 'gold'

jdbc =  os.environ.get('POSTGRE_JDBC')
host =  os.environ.get('POSTGRE_HOST')
dbname = os.environ.get('POSTGRE_DBNAME')
user =  os.environ.get('POSTGRE_USER')
password =  os.environ.get('POSTGRE_PASSWORD')
table = os.environ.get('POSTGRE_TABLE')
port = os.environ.get('POSTGRE_PORT')

create_table_sql = '''
CREATE TABLE IF NOT EXISTS property (
    url VARCHAR,
    description TEXT,
    id VARCHAR PRIMARY KEY,
    initial_at VARCHAR,
    price BIGINT,
    price_currency VARCHAR,
    price_string VARCHAR,
    property_type VARCHAR,
    publish_at VARCHAR,
    site VARCHAR,
    thumbnail VARCHAR,
    title VARCHAR,
    update_at VARCHAR,
    initial_date VARCHAR,
    agent_address VARCHAR,
    agent_agent_type VARCHAR,
    agent_email VARCHAR,
    agent_name VARCHAR,
    agent_phone_number VARCHAR,
    agent_profile VARCHAR, 
    attr_area FLOAT,
    attr_bathroom INTEGER,
    attr_bedroom INTEGER,
    attr_built_year INTEGER,
    attr_certificate VARCHAR,
    attr_condition VARCHAR,
    attr_direction VARCHAR,
    attr_feature VARCHAR,
    attr_floor FLOAT,
    attr_floor_num FLOAT,
    attr_height FLOAT,
    attr_interior VARCHAR,
    attr_length FLOAT,
    attr_site_id VARCHAR,
    attr_total_area FLOAT,
    attr_total_room INTEGER,
    attr_type_detail VARCHAR,
    attr_width FLOAT,
    location_address VARCHAR,
    location_city VARCHAR,
    location_description VARCHAR,
    location_dist VARCHAR,
    location_lat FLOAT,
    location_long FLOAT,
    location_street VARCHAR,
    location_ward VARCHAR,
    project_name VARCHAR,
    project_profile VARCHAR,
    image TEXT
);
'''

def create_postgre_connection():
    postgre_conn = None
    try:
        postgre_conn = SparkSession.builder\
                        .config("spark.jars.packages", "org.postgresql:postgresql:42.2.6") \
                        .appName("PySpark_Postgres")\
                        .getOrCreate()
        print("Postgres connection created successfully!")
    except Exception as e:
        print(f"Couldn't create the spark session due to exception {e}")
        
    return postgre_conn

def create_table_postgre():
    conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password
    )
    cursor = conn.cursor()
    try:
    # Execute the SQL statement
        cursor.execute(create_table_sql)
        # Commit the transaction
        conn.commit()
        print("Table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
    conn.close()
    

def load_data_into_postgre(sparkdf):
    sparkdf.write.format("jdbc")\
            .option("url", jdbc) \
            .option("dbtable",table )\
            .option("user", user)\
            .option("password", password)\
            .option("driver", "org.postgresql.Driver")\
            .mode("append")\
            .save()

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
        s3.head_bucket(Bucket=GOLD_BUCKET)
    except:
        raise Exception("Gold bucket not exist")
        
    print("S3 connection created successfully!")
    return s3

def get_folder_not_in_gold():
    gold_respose = s3.list_objects_v2(Bucket=GOLD_BUCKET, Prefix='', Delimiter='/')
    gold_folder_names =set(prefix.get('Prefix') for prefix in gold_respose.get('CommonPrefixes', []))
    
    return list(gold_folder_names)

def check_date_not_in_postgres(folder_names):
    conn = psycopg2.connect(
            host=host,
            port=port,
            database=dbname,
            user=user,
            password=password
    )
    cursor = conn.cursor() 
    checked_date = []
    for folder in folder_names:
        date = folder.split("/")[0]
        cursor.execute(f"select count(*) from {table} where initial_date = '{date}' ")
        num = cursor.fetchall()[0][0]
        if num == 0:
            checked_date.append(folder)
    cursor.close()
    return checked_date
            

def create_Schema():
    schema = StructType([
        StructField("url", StringType(), True),
        StructField("description", StringType(), True),
        StructField("id", StringType(), True),
        StructField("initial_at", StringType(), True),
        StructField("price", LongType(), True),
        StructField("price_currency", StringType(), True),
        StructField("price_string", StringType(), True),
        StructField("property_type", StringType(), True),
        StructField("publish_at", StringType(), True),
        StructField("site", StringType(), True),
        StructField("thumbnail", StringType(), True),
        StructField("title", StringType(), True),
        StructField("update_at", StringType(), True),
        StructField("initial_date", StringType(), True),
        StructField("agent_address", StringType(), True),
        StructField("agent_agent_type", StringType(), True),
        StructField("agent_email", StringType(), True),
        StructField("agent_name", StringType(), True),
        StructField("agent_phone_number", StringType(), True),
        StructField("agent_profile", StringType(), True),
        StructField("attr_area", FloatType(), True),
        StructField("attr_bathroom", IntegerType(), True),
        StructField("attr_bedroom", IntegerType(), True),
        StructField("attr_built_year", IntegerType(), True),
        StructField("attr_certificate", StringType(), True),
        StructField("attr_condition", StringType(), True),
        StructField("attr_direction", StringType(), True),
        StructField("attr_feature", StringType(), True),
        StructField("attr_floor", FloatType(), True),
        StructField("attr_floor_num", FloatType(), True),
        StructField("attr_height", FloatType(), True),
        StructField("attr_interior", StringType(), True),
        StructField("attr_length", FloatType(), True),
        StructField("attr_site_id", StringType(), True),
        StructField("attr_total_area", FloatType(), True),
        StructField("attr_total_room", IntegerType(), True),
        StructField("attr_type_detail", StringType(), True),
        StructField("attr_width", FloatType(), True),
        StructField("location_address", StringType(), True),
        StructField("location_city", StringType(), True),
        StructField("location_description", StringType(), True),
        StructField("location_dist", StringType(), True),
        StructField("location_lat", FloatType(), True),
        StructField("location_long", FloatType(), True),
        StructField("location_street", StringType(), True),
        StructField("location_ward", StringType(), True),
        StructField("project_name", StringType(), True),
        StructField("project_profile", StringType(), True),
        StructField("image", StringType(), True)
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
                .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.2.2,org.postgresql:postgresql:42.2.6")\
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



def connect_to_minIO(spark_conn,folder_name):
    spark_df = None
    s3_path = f"s3a://{GOLD_BUCKET}/{folder_name}/flat"
    try:
        schema = create_Schema()
        spark_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_path)
        print("MinIO data extracted successfully")
    except Exception as e:
        print(f"MinIO dataframe could not be created because: {e}")
    
    return spark_df

if __name__ == "__main__":
    # create spark connection                                                                                                                                                                                                                                        
    spark_conn = create_spark_connection()
    s3 = create_s3_connection()
    print("Processing start .....")
    if spark_conn is not None:
        create_table_postgre()
        schema = create_Schema()
        folder_names = get_folder_not_in_gold()
        folder_names = check_date_not_in_postgres(folder_names)
        if len(folder_names) != 0:
            for folder in folder_names:
                try:
                    spark_df = connect_to_minIO(spark_conn,folder)
                    load_data_into_postgre(spark_df)
                    print("loaded data into postgre successfully")
                except Exception as e:
                    print("An error occured:",e)
        else:
            print("nothing to load")
    print("Processing end .....")
    spark_conn.stop()





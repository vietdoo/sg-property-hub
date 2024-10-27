import boto3
import os
import psycopg2
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType,StructField,StringType,IntegerType,FloatType,ArrayType,IntegerType,LongType

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

create_house_table = '''
CREATE TABLE IF NOT EXISTS house (
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
    images TEXT[]
);
'''
create_location_table = '''
CREATE TABLE IF NOT EXISTS location (
    id VARCHAR PRIMARY KEY,
    address VARCHAR,
    city VARCHAR,
    description VARCHAR,
    dist VARCHAR,
    lat FLOAT,
    long FLOAT,
    street VARCHAR,
    ward VARCHAR
);
'''

create_attr_table = '''
CREATE TABLE IF NOT EXISTS attr (
    id VARCHAR PRIMARY KEY,
    area FLOAT,
    bathroom INTEGER,
    bedroom INTEGER,
    built_year INTEGER,
    certificate VARCHAR,
    condition VARCHAR,
    direction VARCHAR,
    feature VARCHAR,
    floor FLOAT,
    floor_num FLOAT,
    height FLOAT,
    interior VARCHAR,
    length FLOAT,
    site_id VARCHAR,
    total_area FLOAT,
    total_room INTEGER,
    type_detail VARCHAR,
    width FLOAT
);
'''

create_agent_table = '''
CREATE TABLE IF NOT EXISTS agent (
    id VARCHAR PRIMARY KEY,
    address VARCHAR,
    agent_type VARCHAR,
    email VARCHAR,
    name VARCHAR,
    phone_number VARCHAR,
    profile VARCHAR
);
'''

create_project_table = '''
CREATE TABLE IF NOT EXISTS project (
    id VARCHAR PRIMARY KEY,
    name VARCHAR,
    profile VARCHAR
);
'''
def create_house_schema():
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
        StructField("images", ArrayType(StringType(), True), True),
    ])
    return schema

def create_attr_schema():
    schema = StructType([
        StructField("id", StringType(), True),
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
    ])
    return schema

def create_location_schema():
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("address", StringType(), True),
        StructField("city", StringType(), True),
        StructField("description", StringType(), True),
        StructField("dist", StringType(), True),
        StructField("lat", FloatType(), True),
        StructField("long", FloatType(), True),
        StructField("street", StringType(), True),
        StructField("ward", StringType(), True),
    ])
        
    return schema

def create_agent_schema():
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("address", StringType(), True),
        StructField("agent_type", StringType(), True),
        StructField("email", StringType(), True),
        StructField("name", StringType(), True),
        StructField("phone_number", StringType(), True),
        StructField("profile", StringType(), True),
    ])
    return schema

def create_project_schema():
    schema = StructType([
        StructField("id", StringType(), True),
        StructField("name", StringType(), True),
        StructField("profile", StringType(), True),
    ])
        
    return schema

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
        cursor.execute(create_house_table)
        # Commit the transaction
        conn.commit()
        print("house table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
        
    try:
    # Execute the SQL statement
        cursor.execute(create_attr_table)
        # Commit the transaction
        conn.commit()
        print("attr table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
        
    try:
    # Execute the SQL statement
        cursor.execute(create_location_table)
        # Commit the transaction
        conn.commit()
        print("location table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
        
    try:
    # Execute the SQL statement
        cursor.execute(create_agent_table)
        # Commit the transaction
        conn.commit()
        print("agent table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
        
    try:
    # Execute the SQL statement
        cursor.execute(create_project_table)
        # Commit the transaction
        conn.commit()
        print("project table created successfully!")
    except Exception as e:
        # Rollback in case of error
        conn.rollback()
        print(f"An error occurred: {e}")
    conn.close()

def load_data_into_postgre(spark_house_df,spark_attr_df,spark_location_df,spark_project_df,spark_agent_df):
    print("--------------------------------------------------------------------")
    try:
        spark_house_df.write.format("jdbc")\
                .option("url", jdbc) \
                .option("dbtable", "house")\
                .option("user", user)\
                .option("password", password)\
                .option("driver", "org.postgresql.Driver")\
                .mode("append")\
                .save()
        print("loaded house data into postgre successfully")
    except Exception as e:
        print("loading house data has error: ",e)
        
    try:
        spark_project_df.write.format("jdbc")\
                .option("url", jdbc) \
                .option("dbtable", "project")\
                .option("user", user)\
                .option("password", password)\
                .option("driver", "org.postgresql.Driver")\
                .mode("append")\
                .save()
        print("loaded project data into postgre successfully")
    except Exception as e:
        print("loading project data has error: ",e)
        
    try:
        spark_attr_df.write.format("jdbc")\
                .option("url", jdbc) \
                .option("dbtable", "attr")\
                .option("user", user)\
                .option("password", password)\
                .option("driver", "org.postgresql.Driver")\
                .mode("append")\
                .save()
        print("loaded attr data into postgre successfully")
    except Exception as e:
        print("loading attr data has error: ",e)
        
    try:
        spark_location_df.write.format("jdbc")\
                .option("url", jdbc) \
                .option("dbtable", "location")\
                .option("user", user)\
                .option("password", password)\
                .option("driver", "org.postgresql.Driver")\
                .mode("append")\
                .save()
        print("loaded location data into postgre successfully")
    except Exception as e:
        print("loading location data has error: ",e)
 
    try:
        spark_agent_df.write.format("jdbc")\
                .option("url", jdbc) \
                .option("dbtable", "agent")\
                .option("user", user)\
                .option("password", password)\
                .option("driver", "org.postgresql.Driver")\
                .mode("append")\
                .save()
        print("loaded agent data into postgre successfully")
    except Exception as e:
        print("loading agent data has error: ",e)
        

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
        cursor.execute(f"select count(*) from house where initial_date = '{date}' ")
        num = cursor.fetchall()[0][0]
        if num == 0:
            checked_date.append(folder)
    cursor.close()
    return checked_date

def get_folder_not_in_gold():
    gold_respose = s3.list_objects_v2(Bucket=GOLD_BUCKET, Prefix='', Delimiter='/')
    gold_folder_names =set(prefix.get('Prefix') for prefix in gold_respose.get('CommonPrefixes', []))
    
    return list(gold_folder_names)

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
    s3_house_path = f"s3a://{GOLD_BUCKET}/{folder_name}/house"
    try:
        schema = create_house_schema()
        spark_house_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_house_path)
        print(f"house data extracted successfully")
    except Exception as e:
        print(f"dataframe could not be created because: {e}")
        
    s3_attr_path = f"s3a://{GOLD_BUCKET}/{folder_name}/attr"
    try:
        schema = create_attr_schema()
        spark_attr_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_attr_path)
        print(f"attr data extracted successfully")
    except Exception as e:
        print(f"dataframe could not be created because: {e}")
        
    s3_location_path = f"s3a://{GOLD_BUCKET}/{folder_name}/location"
    try:
        schema = create_location_schema()
        spark_location_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_location_path)
        print(f"location data extracted successfully")
    except Exception as e:
        print(f"dataframe could not be created because: {e}")
        
    s3_agent_path = f"s3a://{GOLD_BUCKET}/{folder_name}/agent"
    try:
        schema = create_agent_schema()
        spark_agent_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_agent_path)
        print(f"agent data extracted successfully")
    except Exception as e:
        print(f"dataframe could not be created because: {e}")
        
    s3_project_path = f"s3a://{GOLD_BUCKET}/{folder_name}/project"
    try:
        schema = create_project_schema()
        spark_project_df = spark_conn.read\
                    .schema(schema)\
                    .parquet(s3_project_path)
        print(f"MinIO project data extracted successfully")
    except Exception as e:
        print(f"MinIO dataframe could not be created because: {e}")
        
        
    return spark_house_df,spark_attr_df,spark_location_df,spark_project_df,spark_agent_df
  
if __name__ == "__main__":
    # create spark connection                                                                                                                                                                                                                                        
    spark_conn = create_spark_connection()
    s3 = create_s3_connection()
    print("Processing start .....")
    if spark_conn is not None:
        create_table_postgre()
        folder_names = get_folder_not_in_gold()
        folder_names = check_date_not_in_postgres(folder_names)
        if len(folder_names) != 0:
            for folder in folder_names:
                print(f"=================================={folder}========================================")
                try:
                    spark_house_df,spark_attr_df,\
                    spark_location_df,spark_project_df,\
                    spark_agent_df = connect_to_minIO(spark_conn,folder)
                    load_data_into_postgre(spark_house_df,spark_attr_df,spark_location_df,spark_project_df,spark_agent_df)
                    print("loaded data into postgre successfully")
                except Exception as e:
                    print("An error occured:",e)
    print("Processing end .....")
    spark_conn.stop()
from pyspark.sql import SparkSession
import random
import string
import pymongo
import os
import boto3
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
import pyarrow as pa

MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY')
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY')
MINIO_HOST = os.environ.get('MINIO_HOST')
MONGO_URL = os.environ.get('MONGO_URL')
MONGO_DB = os.environ.get('MONGO_DB')
MONGO_COLLECTION = os.environ.get('MONGO_COLLECTION')

BRONZE_BUCKET = 'bronze'
LIMIT = 100000
START_DATE = datetime(2023, 10, 26)
END_DATE = datetime.now()

SCHEMA = pa.schema([
    ("url", pa.string(), False),
    ("agent", pa.struct([
        ("address", pa.string(), True),
        ("agent_type", pa.string(), True),
        ("email", pa.string(), True),
        ("name", pa.string(), True),
        ("phone_number", pa.string(), True),
        ("profile", pa.string(), True)
    ]), True),
    ("attr", pa.struct([
        ("area", pa.float32(), True),
        ("bathroom", pa.int32(), True),
        ("bedroom", pa.int32(), True),
        ("built_year", pa.int32(), True),
        ("certificate", pa.string(), True),
        ("condition", pa.string(), True),
        ("direction", pa.string(), True),
        ("feature", pa.string(), True),
        ("floor", pa.float32(), True),
        ("floor_num", pa.float32(), True),
        ("height", pa.float32(), True),
        ("interior", pa.string(), True),
        ("length", pa.float32(), True),
        ("site_id", pa.string(), True),
        ("total_area", pa.float32(), True),
        ("total_room", pa.int32(), True),
        ("type_detail", pa.string(), True),
        ("width", pa.float32(), True)
    ]), True),
    ("description", pa.string(), False),
    ("id", pa.string(), False),
    ("images", pa.list_(pa.string()), True),
    ("initial_at", pa.string(), False),
    ("location", pa.struct([
        ("address", pa.string(), True),
        ("city", pa.string(), True),
        ("description", pa.string(), True),
        ("dist", pa.string(), True),
        ("lat", pa.float32(), True),
        ("long", pa.float32(), True),
        ("street", pa.string(), True),
        ("ward", pa.string(), True)
    ]), True),
    ("price", pa.int64(), True),
    ("price_currency", pa.string(), False),
    ("price_string", pa.string(), True),
    ("project", pa.struct([
        ("name", pa.string(), True),
        ("profile", pa.string(), True)
    ]), True),
    ("property_type", pa.string(), False),
    ("publish_at", pa.string(), True),
    ("site", pa.string(), False),
    ("thumbnail", pa.string(), True),
    ("title", pa.string(), False),
    ("update_at", pa.string(), False),
    ("initial_date", pa.string(), True)
])

def create_s3_connection():
    s3 = boto3.client(
        's3',
        endpoint_url = MINIO_HOST,
        aws_access_key_id = MINIO_ACCESS_KEY,
        aws_secret_access_key = MINIO_SECRET_KEY,
        region_name='us-east-1'
    )

    # Create bucket if not exists
    if not s3.list_buckets()['Buckets']:
        s3.create_bucket(Bucket = BRONZE_BUCKET)

    return s3

def delete_s3_folder(s3, bucket_name, prefix):
    objects_to_delete = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    if 'Contents' in objects_to_delete:
        for obj in objects_to_delete['Contents']:
            s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
    s3.delete_object(Bucket=bucket_name, Key=prefix)

def get_filenames_in_s3_bucket(s3):
    bronze_folders = []
    try:
        for obj in s3.list_objects(Bucket = BRONZE_BUCKET)['Contents']:
            bronze_folders.append(obj['Key'])
    except Exception as e:
        print(f'Error listing objects: {e}')
    return bronze_folders
    
def create_mongo_connection():
    client = pymongo.MongoClient(MONGO_URL)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection


print('Starting load to bronze job')

def load_to_bronze(mode = 'normal'):
    count_total_processed = 0
    count_total_uploaded = 0
    collection = create_mongo_connection()
    s3 = create_s3_connection()
    bronze_folders = get_filenames_in_s3_bucket(s3)
    END_DATE = datetime.now()
    print(f'START_DATE = {START_DATE.strftime("%Y-%m-%d")} -------- END_DATE = {END_DATE.strftime("%Y-%m-%d")}')
    print('---------------------------------------------------------------')
    current_date = START_DATE
    while current_date <= END_DATE:
        query_date = str(current_date.strftime("%Y-%m-%d")) 
        current_date += timedelta(days = 1)

        num_documents = collection.count_documents({'initial_date': query_date})
        if not num_documents:
            continue

        offset = 0
        print(f'Date: {query_date}, Total documents found: {num_documents}')
        id = 0

        
        try:
            if mode == 'force':
                delete_s3_folder(s3, BRONZE_BUCKET, f'{query_date}/')
                print(f'Deleted folder: {BRONZE_BUCKET}/{query_date}/')
        except Exception as e:
            print(f'Error deleting folder: {e}')

        while offset < num_documents:
            num_this_batch = LIMIT if offset + LIMIT < num_documents else num_documents - offset
            count_total_processed += num_this_batch
            file_name = f'part-{id}.parquet'
            print(f'Batch id {id}: {num_this_batch} documents', end = ' \t ')
            if f'{query_date}/{file_name}' in bronze_folders and mode == 'normal':
                print(f'File already exists: {BRONZE_BUCKET}/{query_date}/{file_name}')
                id = id + 1
                offset += LIMIT
                continue
            count_total_uploaded += num_this_batch
            
           
            batch_cursor = collection.find({'initial_date': query_date}, {'_id': 0}).skip(offset).limit(LIMIT)
            offset += LIMIT
            
            batch_data = list(batch_cursor)
            df = pd.DataFrame(batch_data)
            
            for field in SCHEMA:
                if field.name not in df.columns:
                    df[field.name] = None

            buffer = BytesIO()
            df.to_parquet(buffer, schema = SCHEMA, engine = 'pyarrow')
            buffer.seek(0)

            s3.upload_fileobj(buffer, BRONZE_BUCKET, f'/{query_date}/{file_name}')
            print(f'Uploaded to s3: {BRONZE_BUCKET}/{query_date}/{file_name}')
            id = id + 1
        print('---------------------------------------------------------------')
    print(f'Processed {count_total_processed} documents')
    print(f'Uploaded {count_total_uploaded} documents')


import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    #add mode -f 
    parser.add_argument("-f", "--force", help="force run", action="store_true")
    args = parser.parse_args()
    if args.force:
        load_to_bronze(mode = 'force')
    else:
        # load_to_bronze(mode = 'force')
        load_to_bronze()



import hashlib
import os
import pytz
import urllib
import redis
import boto3
import pymongo
import requests
import datetime
import random
import pillow_avif
import logging
import json
from bson.objectid import ObjectId

from celery import chain, group
from celery.signals import worker_process_init
from celery.signals import worker_process_shutdown

from PIL import Image
from pymongo import UpdateOne


from .celery import app
from .celeryconfig import config
from .function.crawler import crawler, validate_item

logger = app.log.get_default_logger()
logger.setLevel(logging.INFO)
db_index = None
s3 = None
s3_image_bucket = None
mongo_raw_items_collection = None

redis_client = None


@worker_process_init.connect
def init_worker(**kwargs):
    logger.info('Initializing worker process')
    global db_index
    global mongo_raw_items_collection
    global redis_client
    global production_client

    redis_client = redis.Redis.from_url(config['redis']['host'])

    db_client = pymongo.MongoClient(config['mongodb']['connection_string'])
    db_index = db_client[config['mongodb']['database']]
    mongo_raw_items_collection = db_index[config['mongodb']
                                          ['raw_products_collection']]
    # mongo_raw_items_collection.create_index('url', unique = True)

    logger.info('Worker process initialized')



@worker_process_shutdown.connect
def worker_shutdown(**kwargs):
    logger.info('Worker process is shutting down...')

@app.task(bind=True)
def crawl_url_list(self, site = None, url = None, mode = 'basic', crawl_only = True, read_file = False):
    global redis_client
    logger.info(f'Crawling item URL list from {site} {url} {mode}')
    if site not in crawler:
        raise Exception('Site not found')

    try:    
        if read_file:
            #txt file contain urls
            file_path = read_file
            with open(file_path) as f:
                urls_file = f.readlines()
            urls_file = [x.strip() for x in urls_file][:500000]
            print(f'Found {len(urls_file)} items')
            urls = []
            for item_url in urls_file:
                # if not redis_client.sismember('celery_url_list', item_url):
                urls.append(item_url)
            
            (group(crawl_item.s(site, url, crawl_only) for url in urls))()

            return 'crawl from file call success with ' + str(len(urls)) + ' urls'

        result = crawler[site]['list'](url)
        urls = []
        for item_url in result['urls']:
            if not redis_client.sismember('celery_url_list', item_url):
                urls.append(item_url)
   
        logger.info(f'Found {len(urls)} items')
        (group(crawl_item.s(site, url, crawl_only) for url in urls))()

        if mode == 'basic':
            if not len(urls):
                return f"{mode} | {url}"
        
        if mode == 'ddos':
            return f"{mode} | {url}"
        
        if result['next_page']:
            crawl_url_list.delay(site, result['next_page'], mode, crawl_only)

        return result
    except Exception as e:
        logger.error('Error when crawling URL list' + str(e))
        raise self.retry(countdown = 120, max_retries = 1)

@app.task(bind=True)
def crawl_item(self, site, url, save_local = False):
    global redis_client

    logger.info(f'Fetching item from {url}')
    if site not in crawler: 
        raise Exception('Site not found')
    try:
        if redis_client.sismember('celery_url_list', url):
            raise Exception(f'Item already crawled')
        item = crawler[site]['item'](url)
        if item == 404:
            raise Exception('Item not found [404]')
        
        id = hashlib.sha1(item['url'].encode('utf-8')).hexdigest()
        item['id'] = id

        item['initial_at'] = datetime.datetime.now(
            pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d %H:%M:%S")
        item['initial_date'] = item['initial_at'][:10]
        item['update_at'] = datetime.datetime.now(
            pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d %H:%M:%S")

        try:
            item['thumbnail'] = item['images'][0]
        except:
            item['thumbnail'] = None

        try:
            if 'price_string' not in item and 'price' in item:
                item['price_string'] = f'{item["price"]} {item["price_currency"]}'
        except Exception as e:
            logger.error('Error when handle price_string' + str(e))

        item = validate_item(item).dict()

        if not save_local:
            chain(load_to_mongo.s(item),
                    )()
        else:
            chain(load_to_local.s(item),
                    )()
    
        return item

    except Exception as e:
        # raise Exception('Error when crawling item' + str(e))
        logger.error('Error when crawling item' + str(e))
        raise self.retry(countdown=120, max_retries = 0)


@app.task
def load_to_mongo(item):
    global redis_client
    '''Save item to database

    Args:
        item (dict): Item to save

    Raises:
        Exception: Error when saving to database
    '''

    logger.info(f'Saving item {item["title"]} to database')
    try:
        db_item = mongo_raw_items_collection.find_one_and_update(
            {'url': item['url']}, {'$set': item}, upsert=True, return_document=True)
        
        # Add to redis after successfully saved to mongo
        redis_client.sadd('celery_url_list', item['url'])
        del db_item['_id']
        
        return db_item
    
    except Exception as e:
        raise Exception('Error when saving to database' + str(e))
    
@app.task
def load_to_local(item):
    global redis_client
    '''Save item to database

    Args:
        item (dict): Item to save

    Raises:
        Exception: Error when saving to database
    '''

    logger.info(f'Saving item {item["title"]} to database')
    try:
        #save to each item to a json file in folder name by date

        today = datetime.datetime.now(
            pytz.timezone('Australia/Sydney')).strftime("%Y-%m-%d")
        root_folder = 'crawler_data'
        if not os.path.exists(root_folder):
            os.makedirs(root_folder)
        folder = f'{root_folder}/{today}'
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        file_name = f'{folder}/{item["id"]}.json'

        with open(file_name, "w") as outfile:
            json.dump(item, outfile, indent = 4)

        return item
    
    except Exception as e:
        raise Exception('Error when saving to database' + str(e))

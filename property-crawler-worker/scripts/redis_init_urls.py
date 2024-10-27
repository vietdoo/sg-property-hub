import redis
import os
import pymongo

REDIS_URL = os.environ.get('CELERY_BROKER_URL')

MONGO_URL=os.environ.get('MONGO_URL')
MONGO_DB=os.environ.get('MONGO_DB')
MONGO_COLLECTION=os.environ.get('MONGO_COLLECTION')

r = redis.Redis.from_url(REDIS_URL)

db_client = pymongo.MongoClient(MONGO_URL)
db = db_client[MONGO_DB]
collection = db[MONGO_COLLECTION]
results = collection.find({})
urls = []

for result in results:
    urls.append(result['url'])

r.sadd('celery_url_list', *urls)
print(f'There are currently {r.scard("celery_url_list")} URLs on Redis')
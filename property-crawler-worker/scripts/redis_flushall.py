import redis
import os

REDIS_URL = os.environ.get('CELERY_BROKER_URL')
r = redis.Redis.from_url(REDIS_URL)
r.flushall()
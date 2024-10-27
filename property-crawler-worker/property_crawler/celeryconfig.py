import os

broker_url = os.environ.get('CELERY_BROKER_URL')
result_backend = os.environ.get('CELERY_RESULT_BACKEND')

timezone = 'Asia/Ho_Chi_Minh'
enable_utc = True
result_expires = 3600
result_cache_max = 10000
worker_redirect_stdouts = False

task_routes = {
    'property_crawler.tasks.crawl_url_list': {'queue': 'crawl_list'},
    'property_crawler.tasks.crawl_item': {'queue': 'crawl_item'},
    'property_crawler.tasks.load_to_mongo': {'queue': 'io'},
    'property_crawler.tasks.load_to_local': {'queue': 'io'},
}

config = {
    'meilisearch': {
        'host': os.environ.get('MEILISEARCH_HOST'),
        'api_key': os.environ.get('MEILISEARCH_API_KEY'),
        'index': os.environ.get('MEILISEARCH_INDEX')
    },
    'mongodb': {
        'connection_string': os.environ.get('MONGO_URL'),
        'database': os.environ.get('MONGO_DB'),
        'raw_products_collection': os.environ.get('MONGO_COLLECTION'),
    },
    'redis': {
        'host': os.environ.get('CELERY_BROKER_URL'),
    },
}

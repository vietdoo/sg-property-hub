from celery import Celery
app = Celery('property_crawler',
             include=['property_crawler.tasks'])
app.config_from_object('property_crawler.celeryconfig')
app.conf.update(
    result_expires=3600,
)
# app.conf.worker_log_level = 'WARNING'
# app.worker_main(['worker', '--loglevel=INFO'])
if __name__ == '__main__':
    app.start()

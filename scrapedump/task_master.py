from __future__ import absolute_import
from celery import Celery

task_master = Celery("scrapedump.celery",
                broker='amqp://',
                backend='amqp://',
                include=['backend.data_loader'],)

task_master.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__=="__main__":
    task_master.start()

from __future__ import absolute_import
from celery import Celery
from project.model import Project

celery = Celery("scrapedump.task_master",
                broker='amqp://',
                backend='amqp://',
                include=['backend.data_loader',
                         'backend.data_exporter'
                        ])

celery.config_from_object('celeryconfig')

if __name__=="__main__":
    celery.start()

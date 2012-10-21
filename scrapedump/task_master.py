from __future__ import absolute_import
from celery import Celery
from celery.schedules import crontab
from utils.exporter import FlatCSVExporter
from utils.exporter import JSONExporter
from project.model import Project

task_master = Celery("scrapedump.task_master",
                broker='amqp://',
                backend='amqp://',
                include=['backend.data_loader',
                         'backend.data_exporter'
                        ])

task_master.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERYBEAT_SCHEDULE = {
        "json_exporter":{
            "task":"run_exporter",
            "schedule":crontab(hour=1),
            "args":(JSONExporter)
        },
        "flat_csv_exporter":{
            "task":"run_exporter",
            "schedule":crontab(hour=1),
            "args":(FlatCSVExporter)
        }
    }
)

if __name__=="__main__":
    task_master.start()

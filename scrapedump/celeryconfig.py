import datetime
from celery.schedules import crontab
from utils.exporter import FlatCSVExporter
from utils.exporter import JSONExporter


CELERY_TASK_RESULT_EXPIRES=3600

CELERYBEAT_SCHEDULE = {
    "json_exporter":{
        "task":"backend.data_exporter.run_exporter",
        "schedule":crontab(hour="*/12"),
        "args":(JSONExporter,)
    },
    "flat_csv_exporter":{
        "task":"backend.data_exporter.run_exporter",
        "schedule":crontab(hour="*/12"),
        "args":(FlatCSVExporter,)
    }
}


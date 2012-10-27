from utils.exporter import JSONExporter
from utils.exporter import FlatCSVExporter
from task_master import celery
from project.model import ProjectList


@celery.task
def run_exporter(exporter):
    project_list = ProjectList()
    for project in project_list.all():
        exporter = exporter(project)
        exporter.run()

@celery.task
def beep(s):
    return s

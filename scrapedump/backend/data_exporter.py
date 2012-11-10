from utils.exporter import JSONExporter
from utils.exporter import FlatCSVExporter
from task_master import celery
from project.model import ProjectList
from project.model import Project


@celery.task
def run_exporter(exporter):
    project_list = ProjectList()
    for project in project_list.all():
        exporter = exporter(project)
        exporter.run()

@celery.task
def beep(s):
    return s

@celery.task
def export_single(project_id,entry_id,export_type):
    project = Project()
    project.get(project_id)
    exporter_list = {'json':JSONExporter,'csv':FlatCSVExporter}
    if export_type == 'json':
        exporter = JSONExporter(project)
    elif export_type == 'csv':
        exporter = FlatCSVExporter(project)
    else:
        raise "bad exporter"
    exporter.export(entry_id)
    

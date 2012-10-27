from utils.exporter import JSONExporter
from utils.exporter import FlatCSVExporter
from task_master import task_master
from project.model import ProjectList


@task_master.task
def run_exporter(exporter):
    project_list = ProjectList()
    for project in project_list.all():
        exporter = exporter(project)
        exporter.run()

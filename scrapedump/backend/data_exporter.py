from utils.exporter import JSONExporter
from utils.exporter import FlatCSVExporter
from utils.exporter import exporters
from task_master import task_master

@task_master.task
def run_json_exporter():
    exporter = JSONExporter()
    exporter.run()

@task_master.task
def run_flatcsv_exporter():
    exporter = FlatCSVExporter
    exporter.run()
        

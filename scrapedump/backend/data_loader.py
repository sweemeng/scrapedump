from project.model import Project
from task_master import celery

@celery.task
def loader_task(project_id,entry,file_id):
    project = Project()
    project.get(project_id)
    project.load_datafile(entry,file_id)
    

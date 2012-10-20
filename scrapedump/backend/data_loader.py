from project.model import Project
from task_master import task_master

@task_master.task
def loader_task(project,entry,file_id):
    project = Project()
    project.get(project)
    project.load_datafile(entry,file_id)
    

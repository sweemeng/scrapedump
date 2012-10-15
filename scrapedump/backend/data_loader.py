from project.model import Project
from celery import Celery

celery = Celery('data_loader',broker='amqp://guest@localhost//')

@celery.task
def loader_task(project,entry,file_id):
    project = Project()
    project.find(project)
    project.load_datafile(entry,file_id)
    

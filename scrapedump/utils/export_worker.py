from project.model import Project
from backend.data_exporter import export_single
import time


def export_worker(msg):
    project = Project()
    project.get(msg['project_id'])
    completed = project.export_completed(msg['entry_id'],msg['format'])
    file_id = ''
    if completed:
        print 'task completed, making sure file need to regenerated'
        metadata = project.get_exported_file(msg['entry_id'],msg['format'])
        if metadata['file_id']:
            f = project.get_datafile(metadata['file_id'])
            uploaded_date = f.upload_date
            last_updated = project.get_entry_updated()
            print uploaded_date
            print last_updated
            if last_updated > uploaded_date:
                print 'file need regen'
                task = export_single.delay(msg['project_id'],msg['entry_id'],msg['format'])
                print task
                project.set_exporter_task(msg['entry_id'],msg['format'],task.id)
                completed = project.export_completed(msg['entry_id'],msg['format'])
    else:
        task = export_single.delay(msg['project_id'],msg['entry_id'],msg['format'])
        project.set_exporter_task(msg['entry_id'],msg['format'],task.id)
        completed = project.export_completed(msg['entry_id'],msg['format'])
           

    while not completed:
        completed = project.export_completed(msg['entry_id'],msg['format'])
        yield {'completed':False,'file_id':file_id,'format':msg['format'],
               'project_id':msg['project_id'],'entry_id':msg['entry_id']}
        time.sleep(1)
    
    project.get(msg['project_id'])
    metadata = project.get_exported_file(msg['entry_id'],msg['format'])
    print metadata['file_id']
    f = project.get_datafile(metadata['file_id'])
    file_id = metadata['file_id']
    yield {'completed':True,'file_id':file_id,'format':msg['format'],
               'project_id':msg['project_id'],'entry_id':msg['entry_id']}



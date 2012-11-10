import json
from project.model import Project
import bson
from backend.data_exporter import export_single
from socketio.namespace import BaseNamespace
from utils.export_worker import export_worker 

class NotifierMixin(BaseNamespace):
    def on_request_file(self,msg):
        exporter = export_worker(msg)
        for result in exporter:
            self.emit('progress',result)
    


from project.model import ProjectModel
import csv
import json

class Exporter(object):
    def __init__(self,project):
        """
            We going to export everything, 
            But to where?
        """
        self.project = project
        self.fs = self.project.get_fs()
    
    def export(self,model):
        raise NotImplemented

    def is_writable(self,entry_id):
        raise NotImplemented
    
    def run(self):
        for entry_id in self.project.entry:
            if is_writable(entry_id):
                self.export(entry_id)
 

class FlatCSVExporter(Exporter):
    def is_writable(self,entry_id):
        black_list = [list,dict]
        model = project.get_entry_collection(entry_id)
        temp = model.all()
        for key in temp[0]:
            if type(temp[0][key]) in black_list:
                return False
        return True
   
    def export(self,entry_id):
        model = self.project.get_entry_collection(entry_id)
        collections = model.all()
        keys = collections[0].keys()
        output =self.fs.new_file()
        csv_output = csv.DictWriter(output,fieldnames=keys)
        for collection in collections:
            csv_output.write(collection)
        self.project.link_exported_file(entry_id,'csv',output._id)


class JsonExporter(Exporter):
    """
        To be honest, not sure if caching it will be really faster
    """
    def is_writable(self,entry_id):
        """
           Hackish
        """ 
        return True    

    def export(self,entry_id)
        model = self.project.get_entry_collection(entry_id)
        collections = model.all()
        output = self.fs.new_file()
        json.dump(output,collections)
        self.project.link_exported_file(entry_id,'json',output._id)

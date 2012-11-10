import csv
import json
import bson
import bson.json_util


class Exporter(object):
    def __init__(self,project):
        """
            We going to export everything, 
            But to where?
        """
        self.project = project
        self.fs = self.project.get_fs()
    
    def export(self,entry_id):
        raise NotImplemented

    def is_writable(self,entry_id):
        raise NotImplemented
    
    def run(self):
        for entry_id in self.project.project.entry:
            if self.is_writable(entry_id):
                self.export(entry_id)
 

class FlatCSVExporter(Exporter):
    def is_writable(self,entry_id):
        black_list = [list,dict]
        model = self.project.get_entry_collection(entry_id)
        temp = model.all()
        for key in temp[0]:
            if type(temp[0][key]) in black_list:
                return False
        return True
   
    def export(self,entry_id):
        print 'exporting'
        model = self.project.get_entry_collection(entry_id)
        entry = self.project.get_entry(entry_id)
        collections = model.all()
        keys = collections[0].keys()
        file_name = entry['name'].replace(' ','_')
        full_name = '%s.csv' % file_name
        output =self.fs.new_file(filename=full_name,content_type='application/csv')
        csv_output = csv.DictWriter(output,fieldnames=keys)
        for collection in collections:
            csv_output.writerow(collection)
        self.project.link_exported_file(entry_id,'csv',output._id)
        output.close()

class JSONExporter(Exporter):
    """
        To be honest, not sure if caching it will be really faster
    """
    def is_writable(self,entry_id):
        """
           Hackish
        """ 
        return True    

    def export(self,entry_id):
        print 'exporting'
        model = self.project.get_entry_collection(entry_id)
        entry = self.project.get_entry(entry_id)
        collections = model.all()
        file_name = entry['name'].replace(' ','_')
        full_name = '%s.json' % file_name
        output = self.fs.new_file(filename=full_name,content_type='application/json')
        json.dump(collections,output,default=bson.json_util.default)
        print 'output is %s ' % output._id
        self.project.link_exported_file(entry_id,'json',output._id)
        output.close()



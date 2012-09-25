from mongomodel import model
from bson.objectid import ObjectId
import gridfs
import copy
from utils import file_handler


# TODO: Find out why does a new field not added into the models
class Project(object):
    def __init__(self):
        self.project_ = 'internal'
        self.collection_ = 'project'
        self.model = model.MongoModel(
                         project=self.project_,
                         collection=self.collection_
        )
        self.project = ProjectTemplate()
    
    def get_api(self):
        api_list = []
        name = self.to_mongo_name()
        for entry in self.project.stats:
            if entry != 'system.indexes':
                print entry
                api_list.append('/api/db/%s/%s/' % (name,self.project.stats[entry]['entry']))
        return api_list 
    
    def get_url(self):
        return '/project/%s/' % (self.project.name.replace(' ','_'))
     
    def create(self,name,description):
        self.project.name = name
        self.project.description = description
        self.save()        
 
    def get(self,id_):
        result = self.model.query({'_id':ObjectId(str(id_))})
        self.project.from_mongo(result)
        return self

    def find(self,name):
        result = self.model.query({'name':name})
        self.project.from_mongo(result)
        return self

    def save(self):
        if self.project.id:
            self.model.update({'_id':ObjectId(str(self.project.id))},self.project.to_mongo())
        else:
            id = self.model.insert(self.project.to_mongo())
            self.project.id = id
    
    def to_mongo_name(self):
        return self.project.name.replace(' ','_')

    def add_entries(self,name):
        if name not in self.project.stats:
            if name and not " " in name:
                data = copy.deepcopy(self.project.stats_template)
                data['entry'] = name
                self.project.stats[name] = data
                self.project.input_file[name] = {}
                self.save()
    
    def get_entries(self):
        mongo_model = model.MongoModel(project=self.to_mongo_name())
        return [model.MongoModel(self.project.name_to_mongo(),entry) for entry in self.project.stats]
    
    def get_db(self):
        project = model.MongoModel(project=self.to_mongo_name())
        return project.db

    def get_stats(self):
        # use the stats variable do not generate new
        temp = []
        for entry in self.project.stats:
            if entry != 'system.indexes':
                mongo_model = model.MongoModel(project=self.to_mongo_name(),collection=self.project.stats[entry]['entry'])
                temp.append((entry,mongo_model.entries.count()))
                # save to stats
                self.project.stats[entry]['count'] = mongo_model.entries.count()
                self.save()
        return self.project.stats
   
    def add_result_file(self,name,file_type='csv'):
        self.project.output_file.append(name)
        self.save()
    
    def get_workers(self):
        return self.project.task_id

    def set_workers(self,task_id):
        self.project.task_id = task_id
        self.save()
    
    def add_datafile(self,entry,datafile):
        # have a reliable way to get file size
        if not file_handler.validator(datafile):
            return ''
        db = self.get_db()
        fs = gridfs.GridFS(db)
        file_id = fs.put(datafile.read())
        data_file = fs.get(file_id)
        input_files = self.project.input_file
        temp = copy.deepcopy(self.project.input_file_template)    
        temp['filename'] = datafile.filename 
        temp['filesize'] = data_file.length
        input_files[entry][str(file_id)] = temp
        self.save()
    
    def get_datafile(self,file_id):
        # return file
        # the flow is we get a project via url
        # then we get via id, the i.e the gridfs way
        db = self.get_db()
        fs = gridfs.GridFS(db)
        file_ = fs.get(file_id)
        return file_
    
    def list_datafile(self,entry):
        # do we store an url?
        pass
    

class ProjectList(object):
    def __init__(self):
        self.project_ = 'internal'
        self.collection_ = 'project'
        self.model = model.MongoModel(
            project=self.project_,
            collection= self.collection_
        )
    
    def all(self):
        result = self.model.all()
        project = Project()
        for entry in result:
            id = str(entry['_id'])
            project.get(id)
            yield project
    
    def list(self):
        result = self.model.all()
        temp = []
        for entry in result:
            project = Project()
            id = str(entry['_id'])
            project.get(id)
            temp.append(project)
        return temp


class ProjectTemplate(object):
    def __init__(self):
        """
           Entry now should an nested document, instead of a few list field
           Adjust related function correctly 
        """
        self.id = ''
        self.name = ''
        self.description = ''
        self.entries = []
        self.task_id = ''
        self.output_file = []
        self.old_count = []
        # it is a stats not data
        self.stats = {}
        self.stats_template = {
                'entry':'',
                'count':0,
                'old_count':0,
                'output_count':0,
                'output_file':[],
                'task_id':'',
            }
        # the key is the entry, 
        # task_id is for celery task for loading data
        self.input_file = {}
        # each entry will be a dict, the key is the gridfs id, 
        self.input_file_template = {
                'filename':'',
                'filesize':'',
                'task_id':''
            }

    def to_mongo(self):
        data = {}
        data['name'] = self.name
        data['description'] = self.description
        data['entries'] = self.entries
        data['task_id'] = self.task_id
        data['output_file'] = []
        data['out_count'] = []
        data['input_file'] = self.input_file
        data['stats'] = self.stats
        return data
    
    def from_mongo(self,data):
        if not data:
            return 
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])

    
    def name_to_mongo(self):
        return self.name.replace(' ','_')
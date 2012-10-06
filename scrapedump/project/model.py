from mongomodel import model
from bson.objectid import ObjectId
import gridfs
import copy
import uuid
from utils import file_handler
from celery.result import AsyncResult

    
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
        print self.project.entry
        for entry in self.project.entry:
            if entry != 'system.indexes':
                print entry
                api_list.append('/api/db/%s/%s/' % (name,self.project.entry[entry]['shortname']))
        return api_list 
    
    def get_entry_api(self,entry_id):
        name = self.to_mongo_name()
        return '/api/db/%s/%s/' % (name,entry_id)
     
    def get_url(self):
        return '/project/%s/' % (self.project.id)
     
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
    
    def add_entry(self,name,description,source,shortname=""):
        # key should be short_name
        # fix unit test for this. 
        # and a few other url library
        # it is add one entry not add to entries
        entry_id = uuid.uuid4()
        entry_id = str(entry_id)
        if not shortname:
            shortname = name.replace(' ','_')

        self.project.entry[entry_id] = copy.deepcopy(self.project.entry_template)
        self.project.entry[entry_id]['description'] = description
        self.project.entry[entry_id]['source'] = source
        # give a nicer default for shorname. It is used in mongo collection name. 
        self.project.entry[entry_id]['shortname'] = shortname
        self.project.entry[entry_id]['url'] = '/project/%s/%s/' % (name,shortname)
        # remove the space check, we will reference back to this
        self.add_stats(entry_id)
        print self.project.to_mongo()
        self.save()
        return entry_id
    
    def get_entries(self):
        return self.project.entry 
    
    def get_entry(self,entry_id):
        temp = {}
        temp.update(self.project.entry[entry_id])
        temp.update(self.project.input_file[entry_id])
        temp.update(self.project.stats[entry_id])
        return temp 
     
    def update_entry(self,entry_id,description,source):
        self.project.entry[entry_id]['description'] = description
        self.project.entry[entry_id]['source'] = source
        self.save()
    
    def get_entry_url(self,entry_id):
        project_id = project.id
        return '/project/%s/%s/' % (project_id,entry_id)

    def add_stats(self,entry_id):
        
        if name not in self.project.stats:
            data = copy.deepcopy(self.project.stats_template)
            data['entry'] = entry_id
            self.project.stats[entry_id] = data
            self.project.input_file[entry_id] = {}
            self.save()
    
    def get_entries_collections(self):
        # return shortname
        mongo_model = model.MongoModel(project=self.to_mongo_name())
        return [model.MongoModel(self.project.name_to_mongo(),self.project.entry[entry]['shortname']) for entry in self.project.entry]

    def get_entry_collection(self,entry_id):
        entry = self.project.entry[entry_id]
        mongo_model = model.MongoModel(project=self.to_mongo_name(),collection=entry['shortname'])
        return mongo_model
    
    def find_entry(self,name):
        entries = self.project.entry
        for entry in entries:
            if entries[entry]['name'] == name:
                return entry
        return None
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
    
    def add_datafile(self,entry_id,datafile):
        # have a reliable way to get file size
        if not file_handler.validator(datafile):
            raise InvalidFileTypeException('Only CSV/JSON file is handled')
        db = self.get_db()
        fs = gridfs.GridFS(db)
        if hasattr(datafile,'name'):
            file_id = fs.put(datafile.read())
        elif hasattr(datafile,'filename'):
            file_id = fs.put(datafile.read(),filename=datafile.filename)
        data_file = fs.get(file_id)
        input_files = self.project.input_file
        temp = copy.deepcopy(self.project.input_file_template)    
        temp['filename'] = datafile.filename 
        temp['filesize'] = data_file.length
        input_files[entry_id][str(file_id)] = temp
        self.save()
    
    def get_datafile(self,file_id):
        # return file
        # the flow is we get a project via url
        # then we get via id, the i.e the gridfs way
        db = self.get_db()
        fs = gridfs.GridFS(db)
        file_ = fs.get(ObjectId(file_id))
        return file_
    
    def list_datafile(self,entry):
        # do we store an url?
        pass
    
    def load_datafile(self,entry_id,file_id):
        datasource = self.project.input_file[entry_id][file_id]
        datafile = self.get_datafile(file_id)
        entry_ = self.get_entry_collection(entry_id)
        handler = file_handler.handler_factory(datafile)
        for data in handler.run():
            entry_.insert(data)
        datasource['loaded'] = True
    
    def load_completed(self,entry_id,file_id):
        datasource = self.project.input_file[entry_id][file_id]
        if not datasource['loaded']:
            task = AsyncResult(datasource['task_id'])
            if not task.ready():
                return False
            else:
                datasource['loaded'] = True
                self.save()
        return True
        
    
    def set_load_worker(self,entry_id,file_id,task_id):
        datasource = self.project.input_file[entry_id][file_id]
        datasource['task_id'] = task_id
        self.save()
    
    

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
        # we will need entries detail
        self.entries = []
        self.entry = {}
        self.entry_template = {
            'name':'',
            'description':'',
            'source':'',
            'shortname':'',
            'url':''
        }
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
            }
        # the key is the entry, 
        # task_id is for celery task for loading data
        self.input_file = {}
        # each entry will be a dict, the key is the gridfs id, 
        self.input_file_template = {
                'filename':'',
                'filesize':'',
                'task_id':'',
                'loaded':False
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
        data['entry'] = self.entry
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

class InvalidFileTypeException(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return self.value

from mongomodel import model
from bson.objectid import ObjectId
import gridfs
import copy
import uuid
from utils import file_handler
from celery.result import AsyncResult
import datetime
    
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
        return '/api/db/%s/%s/' % (self.project.id,entry_id)
     
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
    
    def get_id(self):
        return str(self.project.id)

    def find(self,name):
        result = self.model.query({'name':name})
        self.project.from_mongo(result)
        return self
    
    def save(self):
        if self.project.id:
            self.model.update({'_id':ObjectId(str(self.project.id))},self.project.to_mongo())
            self.get(self.project.id) 
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
        if self.find_entry(name):
            raise EntryExistException('entry exist')
        entry_id = uuid.uuid4()
        entry_id = str(entry_id)
        if not shortname:
            shortname = name.replace(' ','_')
     
        self.project.entry[entry_id] = copy.deepcopy(self.project.entry_template)
        self.project.entry[entry_id]['name'] = name
        self.project.entry[entry_id]['description'] = description
        self.project.entry[entry_id]['source'] = source
        # give a nicer default for shorname. It is used in mongo collection name. 
        self.project.entry[entry_id]['shortname'] = shortname
        self.project.entry[entry_id]['url'] = '/project/%s/%s/' % (name,shortname)
        # remove the space check, we will reference back to this
        self.add_stats(entry_id)
        self.project.export[entry_id] = {}
        print self.project.to_mongo()
        self.save()
        return entry_id
    
    def get_entries(self):
        return self.project.entry 
    
    def get_entry(self,entry_id):
        temp = {}
        temp.update(self.project.entry[entry_id])
        temp.update(self.project.input_file[entry_id])
        self.get_stats()
        temp.update(self.project.stats[entry_id])
        return temp 
     
    def update_entry(self,entry_id,description,source):
        self.project.entry[entry_id]['description'] = description
        self.project.entry[entry_id]['source'] = source
        self.save()
    
    def get_entry_url(self,entry_id):
        project_id = project.id
        return '/entry/%s/%s/' % (project_id,entry_id)

    def add_stats(self,entry_id):
        
        if entry_id not in self.project.stats:
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
                mongo_model = self.get_entry_collection(entry)
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
        print "saving %s" % datafile.filename
        if not file_handler.validator(datafile):
            raise InvalidFileTypeException('Only CSV/JSON file is handled')
        db = self.get_db()
        fs = gridfs.GridFS(db)
        if hasattr(datafile,'filename'):
            filename = datafile.filename
            
        elif hasattr(datafile,'name'):
            filename = datafile.name

	if filename.split('.')[-1] == 'json':
            content_type = 'application/json'
        elif filename.split('.')[-1] == 'csv':
            content_type = 'application/csv'
        elif filename.split('.')[-1] == 'tsv':
            content_type = 'application/csv'
        else:
            raise InvalidFileTypeException('Only CSV/JSON file is handled')

        file_id = fs.put(datafile.read(),filename=filename,content_type=content_type)
        data_file = fs.get(file_id)
        input_files = self.project.input_file
        temp = copy.deepcopy(self.project.input_file_template)    
        temp['name'] = filename.replace('.','_')
        temp['filename'] = filename
        temp['content-type'] = data_file.content_type
        temp['size'] = data_file.length
        temp['download'] = '/download/%s/%s/%s/' % (self.project.id,entry_id,file_id)
        temp['delete'] = '/delete/%s/%s/' % (self.project.id,file_id)
        input_files[entry_id][str(file_id)] = temp
        self.save()
        return str(file_id)
    
    def get_datafile(self,file_id):
        # return file
        # the flow is we get a project via url
        # then we get via id, the i.e the gridfs way
        db = self.get_db()
        fs = gridfs.GridFS(db)
        file_ = fs.get(ObjectId(file_id))
        return file_
    
    def get_datafile_metadata(self,entry_id,file_id):
        temp = self.project.input_file[entry_id][file_id]
        return temp

    def list_datafile_metadata(self,entry_id):
        temp = self.project.input_file[entry_id]
        return temp
    
    def load_datafile(self,entry_id,file_id):
        datasource = self.project.input_file[entry_id][file_id]
        datafile = self.get_datafile(file_id)
        entry_ = self.get_entry_collection(entry_id)
        handler = file_handler.handler_factory(datafile)
        for data in handler.run():
            entry_.insert(data)
        datasource['loaded'] = True
        self.entry_updated()
    
    def delete_datafile(self,entry_id,file_id):
        db = self.get_db()
        fs = gridfs.GridFS(db)
        fs.delete(file_id)
        del self.input_file[entry_id][file_id]
        self.save()
    
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
 
    def get_fs(self):
        db = self.get_db()
        fs = gridfs.GridFS(db)
        return fs
       
    def link_exported_file(self,entry_id,format_,file_id):
        if entry_id not in self.project.export:
            self.project.export[entry_id] = {}
        self.project.export[entry_id][format_]={'file_id':file_id,'task_id':''}
        print 'saving result'
        self.save()
   
    def set_exporter_task(self,entry_id,format_,task_id):
        if not entry_id in self.project.export:
            self.project.export[entry_id] = {}
        if not format_ in self.project.export[entry_id]:
            self.project.export[entry_id][format_] = {'file_id':'','task_id':''}
        self.project.export[entry_id][format_]['task_id'] = task_id
        self.save()
    
    def export_completed(self,entry_id,format_):
        if not self.project.export[entry_id]:
            return False
        
        print self.project.export
        task_id = self.project.export[entry_id][format_]['task_id']
        file_id = self.project.export[entry_id][format_]['file_id']
        if not task_id:
            if not file_id:
                return False
            return True
        task = AsyncResult(task_id)
        if not task.ready():
            return False
        return True
         
    def get_exported_file(self,entry_id,format_):
        return self.project.export[entry_id][format_]
    
    def get_exported_files(self,entry_id):
        return self.project.export[entry_id]
    
    def entry_updated(self):
        self.project.entry_updated = datetime.datetime.utcnow()
        print self.project.entry_updated
        self.save()
    
    def get_entry_updated(self):
        return self.project.entry_updated

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
        self.created_at = None
        self.updated_at = None
        self.entry_updated = None
        self.entry_template = {
            'name':'',
            'description':'',
            'source':'',
            'shortname':'',
            'url':''
        }
        self.task_id = ''
        self.export = {}
        
        # {'entry_id':{'format':'file_id'}}
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
                'name':'',
                'filename':'',
                'filetype':'',
                'content-type':'',
                'size':'',
                'task_id':'',
                'loaded':False,
                'download':'',
                'delete':''
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
        data['export'] = self.export
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        data['entry_updated'] = self.entry_updated
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


class EntryExistException(Exception):
    def __init__(self,value):
        self.value = value
    
    def __str__(self):
        return self.value

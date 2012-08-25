from mongomodel import model
from bson.objectid import ObjectId


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
        for entry in self.project.entries:
            api_list.append('/api/db/%s/%s/' % (name,entry))
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
        if name not in self.project.entries:
            self.project.entries.append(name)
            self.save()
    
    def get_db(self):
        mongo_model = model.MongoModel(project=self.to_mongo_name())
        temp_entries = mongo_model.db.collection_names()
        for entry in temp_entries:
            if entry not in self.project.entries:
                self.create_entries(entry)
        return [model.MongoModel(self.project.name_to_mongo(),entry) for entry in self.project.entries]
    
    def get_stats(self):
        temp = []
        for entry in self.project.entries:
            mongo_model = model.MongoModel(project=self.to_mongo_name(),collection=entry)
            temp.append(entry,mongo_model.entries.count())
        return temp


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
        print temp 
        return temp


class ProjectTemplate(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.description = ''
        self.entries = []
       
    def to_mongo(self):
        data = {}
        data['name'] = self.name
        data['description'] = self.description
        data['entries'] = self.entries
        return data
    
    def from_mongo(self,data):
        if not data:
            return 
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])

        mongo_model = model.MongoModel(project=self.name_to_mongo())
        coll = mongo_model.db.collection_names()
        for c in coll:
            if c not in self.entries:
                self.entries.append(c)
    
    def name_to_mongo(self):
        return self.name.replace(' ','_')

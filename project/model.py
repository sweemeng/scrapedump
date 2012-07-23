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
        return '/api/%s/' % self.project.name.replace(' ','_') 
    
    def get_url(self):
        return '/%s/' % self.project.name.replace(' ','_')
     
    def create(self,name,description):
        self.model.name = name
        self.model.description = description
        self.save()        
 
    def get(self,id):
        result = self.model.query({'_id':ObjectId(str(id))})
        self.project.from_mongo(result)
        return self

    def find(self,name):
        self.model.query({'name':name})

    def save(self):
        id = self.model.insert(self.project.to_mongo())
        self.project.id = id
    
    def to_mongo_name(self):
        return self.project.name.replace('_')


class ProjectList(object):
    def __init__(self):
        self.project_ = 'internal'
        self.collection_ = 'project'
        self.model = MongoModel(
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


class ProjectTemplate(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.description = ''
       
    def to_mongo(self):
        data = {}
        if self.id:
            data['_id'] = ObjectId(str(self.id))
        data['name'] = self.name
        data['description'] = self.description
        return data
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])


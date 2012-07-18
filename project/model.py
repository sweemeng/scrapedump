from mongomodel import model


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
 
    def save(self):
        id = self.model.insert(self.project.to_mongo())
        self.project.id = id


class ProjectTemplate(object):
    def __init__(self):
        self.id = ''
        self.name = ''
        self.description = ''
       
    def to_mongo(self):
        data = {}
        data['name'] = self.name
        data['description'] = self.description
        return data
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])


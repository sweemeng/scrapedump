from mongomodel import model
import bcrypt


class User(object):
    def __init__(self):
        project = 'internal'
        collection = 'user'
        self.model = model.MongoModel(project=project,collection=collection)
        self.user = UserTemplate()
    
    def login(self,username,password):
        temp = self.model.query({'username':username})
        if temp:
            self.user.from_mongo(temp)
            user = self.user
            if not bcrypt.hashpw(password,user.password) == user.password:
                self.user = UserTemplate()
        else:
            self.user = UserTemplate()
        return self

    def create(self,username,password):
        self.user.username = username
        self.user.password = bcrypt.hashpw(password,bcrypt.gensalt())
        self.user.active = True
        self.save()

    def is_active(self):
        return self.user.active

    def is_authenticated(self):
        if self.user.id:
            return True
        return False

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user.id

    def get_api_key(self):
        pass

    def get_project(self):
        pass

    def set_project(self):
        pass

    def save(self):
        id = self.model.insert(self.user.to_mongo())
        self.user.id = str(id)

class UserTemplate(object):
    def __init__(self):
        self.id = ''
        self.username = ''
        self.password = ''
        self.api_key = ''
        self.project = []
        self.active = False

    def to_mongo(self):
        data = {}
        data['username'] = self.username
        data['password'] = self.password
        data['api_key'] = self.api_key
        data['project'] = self.project
        data['active'] = self.active
        return data
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])



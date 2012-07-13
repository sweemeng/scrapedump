from mongomodel import model
import bcrypt
import datetime


class User(object):
    def __init__(self):
        project = 'internal'
        collection = 'user'
        self.model = model.MongoModel(project=project,collection=collection)
        self.user = UserTemplate()
    
    def login(self,username,password):
        pass

    def create(self,username,password):
        self.user.username = username
        self.user.password = bcrypt.hashpw(password,bcrypt.gensalt())
        self.save()

    def get_api_key(self):
        pass

    def get_project(self):
        pass

    def set_project(self):
        pass

    def check_session(self,session_id):
        pass

    def save(self):
        self.model.insert(self.user.to_mongo())

class UserTemplate(object):
    def __init__(self):
        self.id = ''
        self.username = ''
        self.password = ''
        self.api_key = ''
        self.project = []

    def to_mongo(self):
        data = {}
        data['username'] = self.username
        data['password'] = self.password
        data['api_key'] = self.api_key
        data['project'] = self.project
        return data
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])


class SessionTemplate(object):
    def __init__(self):
        self.user_id = ''
        self.session_id = ''
        self.expiry = datetime.datetime.now()
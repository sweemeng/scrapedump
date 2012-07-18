from mongomodel import model
from bson.objectid import ObjectId
import bcrypt
import hashlib


class User(object):
    def __init__(self):
        self.project = 'internal'
        self.collection = 'user'
        self.model = model.MongoModel(
                         project=self.project,
                         collection=self.collection)
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
        auth_token = hashlib.sha224('%s%s' % (username,password))
        self.user.auth_token = auth_token.hexdigest()
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

    def get(self,id):
        temp = self.model.query({'_id':ObjectId(str(id))})
        self.user.from_mongo(temp)
        return self

    def get_auth_token(self):
        return self.user.auth_token

    def get_project(self):
        return self.user.project

    def set_project(self,project):
        self.user.project.append(project)

    def save(self):
        id = self.model.insert(self.user.to_mongo())
        self.user.id = str(id)

class UserTemplate(object):
    def __init__(self):
        self.id = ''
        self.username = ''
        self.password = ''
        self.project = []
        self.active = False
        self.auth_token = ''

    def to_mongo(self):
        data = {}
        data['username'] = self.username
        data['password'] = self.password
        data['project'] = self.project
        data['active'] = self.active
        data['auth_token'] = self.auth_token
        return data
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
                setattr(self,'id',str(data['_id']))
                continue
            setattr(self,key,data[key])



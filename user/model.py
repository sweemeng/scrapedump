from mongomodel import model

class User(object):
    def __init__(self):
        project = 'internal'
        collection = 'user'
        self.model = model.MongoModel(project=project,collection=collection)
        self.user = UserTemplate()
    
    def login(self,username,password):
        pass

    def create_user(self,username,password):
        pass

    def get_api_key(self):
        pass

    def get_project(self):
        pass

    def set_project(self):
        pass

class UserTemplate(object):
    def __init__(self):
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

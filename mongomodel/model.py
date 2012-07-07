import pymongo


class MongoModel(object):
    def __init__(self,project):
        self.conn = pymongo.Connection()
        self.db = self.conn.db
        self.entries = self.db[project]

    def query(self,param):
        return self.entries.find(param)

    def insert(self,data):
        self.entries.insert(data)

    def update(self,param,data):
        self.entries.update(param,data)

    def delete(self,param):
        self.entries.remove(param)




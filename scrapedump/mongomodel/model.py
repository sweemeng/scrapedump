import pymongo


class MongoModel(object):
    # The big idea is to make data more json friendly
    # the exception is the json utils, 
    def __init__(self,project='scraped',collection='default'):
        self.conn = pymongo.Connection()
        self.db = self.conn[project]
        self.entries = self.db[collection]

    def query(self,param,fetch_all=False):
        if fetch_all:
            result = []
            temp = self.entries.find(param)
            for t in temp:
                result.append(t)
        else:
            result = self.entries.find_one(param)
        return result

    def insert(self,data):
        return self.entries.insert(data)

    def update(self,param,data):
        for d in data:
            temp={d:data[d]}
            self.entries.update(param,{'$set':temp})

    def delete(self,param):
        self.entries.remove(param)

    def all(self):
        data= self.entries.find()
        result = []
        for d in data:
            result.append(d)
        return result


class DatabaseList(object):
    def __init__(self):
        self.conn = pymongo.Connection()

    def list_project(self):
        return self.conn.database_names()



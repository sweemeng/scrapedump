import pymongo
import dateutil.parser as dateparser


class MongoModel(object):
    def __init__(self):
        self.conn = pymongo.Connection()
        self.db = self.conn.db
        self.entries = self.db.entries

    def query(self,param):
        return self.entries.find(param)

    def insert(self,data):
        data['_timestamp'] = dateparser.parse(data['_timestamp'])
        self.entries.insert(data)

    def update(self,param,data):
        self.entries.update(param,data)

    def delete(self,param):
        self.entries.remove(param)




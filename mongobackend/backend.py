from pubsub import PubSub
import pymongo
import inspect
from event.event import Event
import dateutil.parser as dateparser


class MongoModel(object):
    def __init__(self):
        self.conn = pymongo.Connection()
        self.db = self.conn.db
        self.entries = self.db.entries

    def query(self,param):
        return self.entries.find(param)

    def insert(self,data):
        data['_date'] = dateparser.parse(data['date'])
        self.entries.insert(data)

    def update(self,param,data):
        self.entries.update(param,data)

    def delete(self,param):
        self.entries.remove(param)


class MongoBackend(object):
    def __init__(self):
        self.pipeline = PubSub('pipeline')
    
    def run(self):
        subscription = self.pipeline.subscribe()
        for entry in subscription:
            model = MongoModel()
            event = Event()
            event.from_json(entry)
            func = getattr(model,event.data)
            params = inspect.getargspec(func)
            if len(params.args) > 2:
                func(event.data,event.param)
            elif len(params.args) == 2:
                func(event.data)
            


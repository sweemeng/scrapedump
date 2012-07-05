import json
import datetime


class Event(object):
    def __init__(self,action=None,data=None,param=None):
        self.action = action
        self.data = data
        self.param = param

    def from_dict(self,data):
        self.action = data['action']
        self.data = data['data']
        self.param = data['param']

    def from_json(self,data):
        data = json.loads(data)
        self.from_dict(data)

    def to_json(self):
        temp = {}
        temp['action'] = self.action
        temp['data'] = self.data
        temp['param'] = self.param
        now = datetime.datetime.now()
        temp['_timestamp'] = now.isoformat()

        return json.dumps(temp)

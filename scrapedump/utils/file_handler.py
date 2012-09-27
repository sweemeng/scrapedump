"""
    This is where we handle data file, 
    Celery worker will rely here to read data file uploaded to grid fs
    File handling and validation will goes here. 
"""

import csv
import json
import cStringIO


class CSVHandler(object):
    def __init__(self,datafile):
        self.dialect = csv.Sniffer().sniff(datafile.read(1024))
        
        datafile.seek(0)
        temp = datafile.read()
        temp_file = cStringIO.StringIO(temp)
        self.data = csv.reader(temp_file,self.dialect)
        self.header = self.data.next()
    
    def run(self):
        for d in self.data:
            temp = zip(self.header,d)
            yield dict(temp)


class JsonHandler(object):
    def __init__(self,datafile):
        self.data = json.load(datafile)
    
    def run(self):
        if type(self.data) == list:
            for d in self.data:
                yield d
        else:
            yield self.data


def validator(datafile):
    handled_filetype = { 'csv':CSVHandler,'json':JsonHandler }
    filename = datafile.filename
    filetype = filename.split('.')[-1]
    return filetype in handled_filetype

def handler_factory(datafile):
    handled_filetype = { 'csv':CSVHandler,'json':JsonHandler }
    filename = datafile.filename
    filetype = filename.split('.')[-1]
    
    if filetype == 'json':
        handler = JsonHandler
    elif filetype == 'csv':
        handler = CSVHandler
    else:
        assert False
    
    return handler(datafile)

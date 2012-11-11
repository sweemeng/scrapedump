from mongomodel.model import MongoModel
import datetime
import uuid

"""
A document is a container for each data
Instead of injecting metadata into data
We put it in a "container", and add meta data around it. 
Bonus point? We can just display data, but not meta data. 

A revision contain changes in a document,  
But will allow us to look at different revision of a data
Once we have versioning, we will need to handle conflict sooner or later
""" 

class Document(object):
    """
        This is only a container,
    """ 
    def __init__(self,project_id,entry_id):
        self.project_id = project_id
        self.entry_id = entry_id
        self.project = Project()
        self.project.get(project_id)
        self.db = self.project.get_entry_collection(entry_id)
        self.document = DocumentTemplate()
    
    def get(self,document_id):
        data = self.db.get(document_id)
        self.document.from_mongo(data)

    def create(self,data,creator):
        self.document.data = data
        self.document.creator = creator
        now = datetime.datetime.utcnow()
        self.document.created_at = now
        self.document.updated_at = now
        temp = {
            'id':uuid.uuid4(),
            'editor':creator,
            'updated_date':now,
            'revision':1,
            'added':{},
            'deleted':{},
            'changed':{}
        }
        self.document.revision.append(temp)
        self.save()
    
    def update(self,data,editor):
        self.get(self.document.id)
        now = datetime.datetime.utcnow()
        latest_revision = self.document.revision[-1]
        next_revision_number = latest_revision['revision'] + 1
        revision_id = uuid.uuid4()
        diff = self.get_diff(self.document.data,data)
        temp = {
            'id':revision_id,
            'editor':editor,
            'updated_data':now,
            'revision':next_revision_number,
            'added':diff['added'],
            'changed':diff['changed'],
            'deleted':diff['deleted']
        }
        self.document.data = data
        self.document.updated_date = now
        self.save()
        
    
    def get_diff(self,original, updated):
        diff = {
            'added':{},
            'changed':{},
            'deleted':{}
        }
        for key in original:
            if key not in updated:
                diff['deleted'][key] = original[key]
            if original[key] != updated[key]:
                diff['changed'][key] = original[key]
        for key in updated:
            if key not in original:
                diff['added'][key] = updated[key]
        return diff
                
    
    def delete(self):
        self.db.delete(self.document.id)
        self.document = DocumentTemplate()
    
    def save(self):
        """
           If project is defined, sure save it, else raise an exception!
        """
        if self.document.id:
            self.db.insert(self.document)
        else:
            self.db.update(self.document.id,self.document)
    
    def to_dict(self):
        """
           If a projectis not defined, put it here, the bonus is, we can use is as json!
        """
        return self.document
    
    def to_json(self):
        """
           Return json
        """
    
    def to_json_data(self):
        """
           data only
        """



class DocumentTemplate(object):
    def __init__(self):
        self.id = ''
        # data can be a list or a dict
        self.data = None
        self.created_date = None
        self.updated_date = None
        self.revision = []
        self.creator = ''
        # we will need a good view for conflict
        self.revision_template = {
            'id':'',
            'revision':'',
            'added':{},
            'removed':{},
            'changed':{},
            'updated_date':None,
            'editor':''
        }
    
    def from_mongo(self,data):
        for key in data:
            if key == '_id':
               self.id = data['_id']
            else:
               setattr(self,key,data[key])
    
    def to_mongo(self):
        data = {}
        data['_id'] = self.id
        data['data'] = self.data
        data['created_date'] = self.created_date 
        data['updated_date'] = self.updated_date
        data['revision'] = self.revision
        data['creator'] = self.creator
        return data

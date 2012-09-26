from nose.tools import with_setup
from mock import MagicMock
import gridfs
from bson.objectid import ObjectId
from project.model import Project
from project.model import ProjectTemplate
from mongomodel.model import MongoModel 
import cStringIO

# add test for project

# make sure there is name, description, entry(ies?)
def test_project_fields():
    project = ProjectTemplate()
    assert hasattr(project,'id')
    assert hasattr(project,'name')
    assert hasattr(project,'description')
    assert hasattr(project,'entries')
    assert type(project.entries) == list

# make crud test
def setup_test_project_create():
    pass

def teardown_test_project_create():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})
   
@with_setup(setup_test_project_create,teardown_test_project_create)
def test_project_create():
    project = Project()
    test_project_name = 'test project db'
    test_project_desc = 'test_project_desc'
    project.create(test_project_name,test_project_desc)
    assert project.project.name == test_project_name
    assert project.project.description == test_project_desc
    assert project.project.entries == []
    db = MongoModel(project='internal',collection='project')
    test_data = db.query({'name':test_project_name})
    assert test_data['name'] == test_project_name
    assert test_data['description'] == test_project_desc
    db.delete({'name':test_project_name})

def setup_test_project_update():
    project = Project()
    project.create('test project update','updating project')

def teardown_test_project_update():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project update'})

@with_setup(setup_test_project_update,teardown_test_project_update)
def test_project_update():
    project = Project()
    project.find('test project update')
    project.project.description = 'project updated'
    project.save()
    db = MongoModel(project='internal',collection='project')
    temp = db.query({'name':'test project update'})
    assert temp['description'] == 'project updated'    

# remember that have multiple entries
def setup_test_project_entries():
    project = Project()
    project.create('test project entries',' list entries')

def teardown_test_project_entries():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project entries'})

@with_setup(setup_test_project_entries,teardown_test_project_entries)
def test_project_entries():
    project = Project()
    project.find('test project entries')
    project.add_entries('test_entries')
    
    db = MongoModel(project='internal',collection='project')
    temp = db.query({'name':'test project entries'})
    assert 'test_entries' in temp['stats'] 

# now also each project need to actually linked to a real db
def setup_test_project_db():
    project = Project()
    project.create('test project db',' list entries')
    project.add_entries('test_entries')

def teardown_test_project_db():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})

@with_setup(setup_test_project_db,teardown_test_project_db)
def test_project_stats():
    project = Project()
    project.find('test project db')
    databases = project.get_stats()
    for database in databases:
        assert database == 'test_entries' 

# now also each project need to actually linked to a real db
def setup_test_project_api():
    project = Project()
    project.create('test project db',' list entries')
    project.add_entries('test_entries')

def teardown_test_project_api():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})

@with_setup(setup_test_project_api,teardown_test_project_api)
def test_project_api():
    project = Project()
    project.find('test project db')
    print project.get_api()
    assert '/api/db/test_project_db/test_entries/' in project.get_api()

def setup_test_project_upload():
    project = Project()
    project.create('test project upload',' list entries')
    project.add_entries('test_entries')

def teardown_test_project_upload():
    project = Project()
    project.find('test project upload') 
    fs = gridfs.GridFS(project.get_db())
    for entry in project.project.input_file:
        for file_id in project.project.input_file[entry]:
            fs.delete(ObjectId(file_id))
    db = MongoModel(project='internal',collection='project')
    
    db.delete({'name':'test project upload'})

def mock_open(filename,data=None):
    mock = MagicMock(spec=file,filename=filename)
    handle = MagicMock(spec=file)
    handle.write.return_value = None
    handle.read.return_value = data.getvalue()
    if data is None:
        handle.__enter__.return_value = handle
    else:
        handle.__enter__.return_value = data
    mock.return_value = handle
    return mock

class MockFile(object):
    def __init__(self,filename,data):
        self.filename = filename
        self.data = data
    
    def read(self):
        return self.data

@with_setup(setup_test_project_upload,teardown_test_project_upload)
def test_project_file_upload():
    content = "a,b,c\n1,2,3\n4,5,6"
    test_data = cStringIO.StringIO(content)
    f = MockFile('test_data.csv',content)
    project = Project()
    project.find('test project upload')
    project.add_datafile('test_entries',f)
    
    input_file = project.project.input_file
    exist_flag = False
    for entry in input_file:
        for file_id in input_file[entry]:
            if input_file[entry][file_id]['filename'] == 'test_data.csv':
                exist_flag = True
    
    assert exist_flag 

def test_project_file_get():
    pass

def test_project_file_list():
    pass

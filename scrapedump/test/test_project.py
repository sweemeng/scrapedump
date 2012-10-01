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
    db.conn.drop_database('test_project_db')
   
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
    db.conn.drop_database('test_project_update')

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
    db.conn.drop_database('test_project_entries')

@with_setup(setup_test_project_entries,teardown_test_project_entries)
def test_project_entries():
    project = Project()
    project.find('test project entries')
    # add_entries now should have a description and name file
    # there should be a short name field, for field name
    # We should have a source
    project.add_entry('test entries','test data','test_entries','test_entries')
    
    db = MongoModel(project='internal',collection='project')
    temp = db.query({'name':'test project entries'})
    assert 'test entries' in temp['stats'] 

# now also each project need to actually linked to a real db
def setup_test_project_db():
    project = Project()
    project.create('test project db',' list entries')
    project.add_entry('test entries','test data','test_entries','test_data')

def teardown_test_project_db():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})
    db.conn.drop_database('test_project_db')

@with_setup(setup_test_project_db,teardown_test_project_db)
def test_project_stats():
    project = Project()
    project.find('test project db')
    databases = project.get_stats()
    print databases
    for database in databases:
        assert database == 'test entries' 

# now also each project need to actually linked to a real db
def setup_test_project_api():
    project = Project()
    project.create('test project db',' list entries')
    project.add_entry('test entry','test data','test_entries','test_entries')

def teardown_test_project_api():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})
    db.conn.drop_database('test_project_db')

@with_setup(setup_test_project_api,teardown_test_project_api)
def test_project_api():
    project = Project()
    project.find('test project db')
    print project.get_api()
    assert '/api/db/test_project_db/test_entries/' in project.get_api()

def setup_test_project_upload():
    project = Project()
    project.create('test project upload',' list entries')
    project.add_entry('test entries','test entries','test_source','test_entries')

def teardown_test_project_upload():
    project = Project()
    project.find('test project upload') 
    fs = gridfs.GridFS(project.get_db())
    for entry in project.project.input_file:
        for file_id in project.project.input_file[entry]:
            fs.delete(ObjectId(file_id))
    db = MongoModel(project='internal',collection='project')
    
    db.delete({'name':'test project upload'})
    db.conn.drop_database('test_project_upload')

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
    
    def read(self,buf=None):
        return self.data[:buf]

@with_setup(setup_test_project_upload,teardown_test_project_upload)
def test_project_file_upload():
    content = "a,b,c\n1,2,3\n4,5,6"
    test_data = cStringIO.StringIO(content)
    f = MockFile('test_data.csv',content)
    project = Project()
    project.find('test project upload')
    project.add_datafile('test entries',f)
    
    input_file = project.project.input_file
    exist_flag = False
    for entry in input_file:
        for file_id in input_file[entry]:
            if input_file[entry][file_id]['filename'] == 'test_data.csv':
                exist_flag = True
    
    assert exist_flag 

def setup_test_project_download():
    project = Project()
    project.create('test project download',' list entries')
    content = "a,b,c\n1,2,3\n4,5,6"
    f = MockFile('test_data.csv',content)
    project.add_entry('test entries','test entry','test_entries','testdata')
    project.add_datafile('test entries',f)

def teardown_test_project_download():
    project = Project()
    project.find('test project download') 
    fs = gridfs.GridFS(project.get_db())
    for entry in project.project.input_file:
        for file_id in project.project.input_file[entry]:
            fs.delete(ObjectId(file_id))
    db = MongoModel(project='internal',collection='project')
    
    db.delete({'name':'test project download'})
    db.conn.drop_database('test_project_download')

@with_setup(setup_test_project_download,teardown_test_project_download)
def test_project_file_download():
    content = "a,b,c\n1,2,3\n4,5,6"
    project = Project()
    project.find('test project download')
    data = project.project.input_file
    files = data['test entries']
    valid_flag = False
    for file_id in files:
        test_file = project.get_datafile(file_id)
        test_data = test_file.read()
        if test_data == content:
            valid_flag = True
    
    assert valid_flag
        
def test_project_file_list():
    pass

def setup_test_load_data():
    project = Project()
    project.create('test load data',' list entries')
    content = "a,b,c\n1,2,3\n4,5,6"
    f = MockFile('test_data.csv',content)
    project.add_entry('test entries','test entries','test_entries','testdata')
    project.add_datafile('test entries',f)
    
def teardown_test_load_data():
    project = Project()
    project.find('test load data') 
    fs = gridfs.GridFS(project.get_db())
    for entry in project.project.input_file:
        for file_id in project.project.input_file[entry]:
            fs.delete(ObjectId(file_id))
    db = MongoModel(project='internal',collection='project')
    
    db.delete({'name':'test load data'})
    db.conn.drop_database('test_load_data')

@with_setup(setup_test_load_data,teardown_test_load_data)
def test_load_data():
    project = Project()
    project.find('test load data')
    datasource = project.project.input_file['test entries']
    key = datasource.keys()[0]
    entry = project.get_entry('test entries')
    print key
    project.load_datafile('test entries',key)
    test_data = entry.query({'a':'1'})
    assert test_data['b'] == '2' 
    assert test_data['c'] == '3'

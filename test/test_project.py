from nose.tools import with_setup
from projectmodel.model import Project
from projectmodel.model import ProjectTemplate
from mongomodel.model import MongoModel 

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
    assert 'test_entries' in temp['entries'] 

# now also each project need to actually linked to a real db
def setup_test_project_db():
    project = Project()
    project.create('test project db',' list entries')
    project.add_entries('test_entries')

def teardown_test_project_db():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'test project db'})

@with_setup(setup_test_project_db,teardown_test_project_db)
def test_project_db():
    project = Project()
    project.find('test project db')
    databases = project.get_db()
    for database in databases:
        assert type(database) == MongoModel

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


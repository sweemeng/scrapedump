import webapp
from nose.tools import with_setup
from user.model import User
from project.model import Project
from project.model import ProjectList
from mongomodel.model import MongoModel

def setup_project_view():
    project = Project()
    project.create('project view','test project view')
    project.add_entry('data','test data','data')

def teardown_project_view():
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'project view'})

@with_setup(setup_project_view,teardown_project_view)
def test_project_view():
    test_client = webapp.app.test_client()
    result = test_client.get('/')
    project = Project()
    project.find('project view')
    assert project.project.id in result.data
    
    result = test_client.get('/project/%s/'% project.project.id)
    assert 'project view' in result.data
    assert 'data' in result.data

def setup_project_create():
    user = User()
    user.create('test_create_user','test_password','test@example.com')

def teardown_project_create():
    user = User()
    user.login('test_create_user','test_password')
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'username':'test_create_user'})
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'project create'})

@with_setup(setup_project_create,teardown_project_create)
def test_project_create():
    test_client = webapp.app.test_client()
    result = test_client.post('/login/',data={
        'username':'test_create_user',
        'password':'test_password'
    },follow_redirects=True)
    
    project_ui = test_client.post('/project/',data={
        'name':'project create',
        'description':'project create',
    },follow_redirects=True) 
    print project_ui.data    
    assert 'project create' in project_ui.data
    assert 'data' in project_ui.data


def setup_project_update():
    user = User()
    user.create('test_update_user','test_password','test@example.com')
    project = Project()
    project.create('project update','test project update')
    user.add_project(project.get_id())
    project.add_entry('data','test data','data')

def teardown_project_update():
    user = User()
    user.login('test_update_user','test_password')
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'username':'test_update_user'})
    db = MongoModel(project='internal',collection='project')
    db.delete({'name':'project update'})

@with_setup(setup_project_update,teardown_project_update)
def test_project_update():
    test_client = webapp.app.test_client()
    result = test_client.post('/login/',data={
        'username':'test_update_user',
        'password':'test_password'
    },follow_redirects=True)
    project = Project()
    project.find('project update') 
    project_ui = test_client.post('/project/%s/' % project.project.id,data={
        'description':'project updated',
    },follow_redirects=True) 
    print project_ui.data
    
    assert 'project updated' in project_ui.data
    assert 'data' in project_ui.data


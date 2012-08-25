import webapp
from user.model import User
from projectmodel.model import Project
from projectmodel.model import ProjectList
from mongomodel.model import MongoModel
from nose.tools import with_setup
import json
from bson.objectid import ObjectId

# Create project, associate with a user
def setup_project():
    data = (
        ('project 1','project content 1'),
        ('project 2','project content 2'),
        ('project 3','project content 3')
    )
    for d in data:
        project = Project()
        project.create(d[0],d[1])    

def teardown_project():
    data = (
        ('project 1','project content 1'),
        ('project 2','project content 2'),
        ('project 3','project content 3')
    )
    for d in data:
        project = Project()
        project.find(d[0])
        model = MongoModel(project=project.project_,collection=project.collection_)
        model.delete({'_id':ObjectId(str(project.project.id))})

@with_setup(setup_project,teardown_project)
def test_project_list():
    # this do not require user auth
    data = (
        ('project 1','project content 1'),
        ('project 2','project content 2'),
        ('project 3','project content 3')
    )
    test_client = webapp.app.test_client()
    result = test_client.get('/api/project/')
    for d in data:
        assert d[0] in result.data
        assert d[1] in result.data
    
@with_setup(setup_project,teardown_project)
def test_project_get():
    # this do not require user auth 
    data = (
        ('project 1','project content 1'),
        ('project 2','project content 2'),
        ('project 3','project content 3')
    )
    
    test_client = webapp.app.test_client()
    
    for d in data:
        project = Project()
        project.find(d[0])
        url = '/api/project/%s/' % (project.project.id)
        result = test_client.get(url)
        assert d[0] in result.data
        assert d[1] in result.data

def setup_user():
    user = User()
    user.create('test_user','test_pass','test@example.com')

def teardown_user():
    user = User()
    user.login('test_user','test_pass')
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':objectid.ObjectId(str(user.user.id))})

# Now anything that need to update db will need to
def setup_test_project_create():
    pass

def teardown_test_project_create():
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project create'})

@with_setup(setup_test_project_create,teardown_test_project_create)
def test_project_create():
    # login user get token
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.auth_token 
    # do a post
    url = '/api/project/?api_key=%s' % api_key
    # now check project in user
    test_client = webapp.app.test_client()
    data = {'name':'project create','description':'project content create'}
    
    result = test_client.post(url,data=json.dumps(data),content_type='application/json')
    status = json.loads(result.data)
    assert status['status']
    project = ProjectList()
    test_user = User()
    test_user.login('test_user','test_pass')
    assert 'project create'.replace(' ','_') in test_user.user.project
    for i in project.all():
        print i.project.name
        assert 'project create' == i.project.name
    
    # now delete it
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project create'})

def setup_project_delete():
    user = User()
    user.create('test_user_delete','test_pass','test@example.com')
    project = Project()
    project.create('project 1','project content 1')
    user.add_project('project_1')

def teardown_project_delete():
    user = User()
    user.login('test_user_delete','test_pass')
    project = Project()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':ObjectId(user.user.id)})
    project.find('project 1')
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project 1'})

@with_setup(setup_project_delete,teardown_project_delete)
def test_project_delete():
    # login user get token
    user = User()
    user.login('test_user_delete','test_pass')
    api_key = user.user.auth_token
    project = Project()
    project.find('project 1')
    # do a delete
    test_client = webapp.app.test_client()
    url = '/api/project/%s/?api_key=%s' % (project.project.id,api_key)
    result = test_client.delete(url)
    status = json.loads(result.data)
    # now check user don't exist
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    data = model.query({'name':'project 1'})
    assert not data

    test_user = User()
    test_user.login('test_user_delete','test_pass')
    assert 'project_1' not in test_user.user.project

    

def setup_user_project():
    # now create user
    user = User()
    user.create('test_user_update','test_pass','test@example.com') 
    # create project
    project = Project()
    project.create('project update','project update content')
    # associate project
    user.add_project('project_update')

def teardown_user_project():
    user = User()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'username':'test_user_update'})
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project update'})
    
@with_setup(setup_user_project,teardown_user_project)
def test_project_update():
    user = User()
    user.login('test_user_update','test_pass')
    api_key = user.user.auth_token
    project = Project()
    project.find('project update')
    test_client = webapp.app.test_client()
    url = '/api/project/%s/?api_key=%s' % (project.project.id,api_key)
    data = json.dumps({'description':'project updated content'})
    result = test_client.put(url,data=data,content_type='application/json')
    status = json.loads(result.data)
    assert status['status']
    
    project=Project()
    project.find('project update')
    assert project.project.description == 'project updated content'

# now project created, you join or withdraw
# you are talking about user info, so go figure
def setup_user_project_list():
    user = User()
    user.create('test_user_list','test_pass','test@example.com')
    project = Project()
    project.create('project list 1','project content 1')
    project = Project()
    project.create('project list 2','project content 2')
    project = Project()
    project.create('project list 3','project content 3')
    user.add_project('project_list_1')
    user.add_project('project_list_2')

def teardown_user_project_list():
    user = User()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'username':'test_user_list'})
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project list 1'})
    model.delete({'name':'project list 2'})
    model.delete({'name':'project list 3'})

# do user join a project, or a project added to user?
@with_setup(setup_user_project_list,teardown_user_project_list)
def test_user_project_list():
    user = User()
    user.login('test_user_list','test_pass')
    api_key = user.user.auth_token
    test_client = webapp.app.test_client()
    data = {'action':'user_list'}
    url = '/api/project/?api_key=%s' % api_key
    result = test_client.get(url)
    print result.data
    assert 'project list 1' in result.data
    assert 'project list 2' in result.data

@with_setup(setup_user_project_list,teardown_user_project_list)
def test_user_project_join():
    user = User()
    user.login('test_user_list','test_pass')
    api_key = user.user.auth_token
    test_client = webapp.app.test_client()
    project = Project()
    project.find('project list 3')
    
    url = '/api/project/%s/?api_key=%s' % (project.project.id,api_key)

    data = {'project':'project list 3','action':'join'}

    result = test_client.put(url,data=json.dumps(data),content_type='application/json')
    user.login('test_user_list','test_pass')
    print user.user.project
    assert 'project_list_3' in user.user.project

@with_setup(setup_user_project_list,teardown_user_project_list)
def test_user_project_withdraw():
    user = User()
    user.login('test_user_list','test_pass') 
    user.add_project('project_list_3')
    api_key = user.user.auth_token
    test_client = webapp.app.test_client()
    project = Project()
    project.find('project list 3')

    url = '/api/project/%s/?api_key=%s' % (project.project.id,api_key)
       
    data = {'project':'project list 3','action':'withdraw'}

    result = test_client.put(url,data=json.dumps(data),content_type='application/json')
    print result.data 
    user.login('test_user_list','test_pass')
    print user.user.project
    assert not 'project_list_3' in user.user.project



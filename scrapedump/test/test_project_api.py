import webapp
from user.model import User
from project.model import Project
from project.model import ProjectList
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
        model.conn.drop_database(d[0].replace(' ','_'))

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
    model.delete({'username':'test_user'})

# Now anything that need to update db will need to
def setup_test_project_create():
    setup_user()

def teardown_test_project_create():
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project create'})
    teardown_user()

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
    print test_user.user.project
    registered = False
    for i in project.all():
        if i.get_id() in test_user.get_project():
            registered = True
    assert registered, "project not in user project"
       
    exist = False
    for i in project.all():
        
        if 'project create' == i.project.name:
            exist = True
    assert exist, "project created"
    
    # now delete it
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project create'})

def setup_project_delete():
    user = User()
    user.create('test_user_delete_api_project','test_pass','test@example.com')
    project = Project()
    project.create('project 1','project content 1')
    user.add_project(project.get_id())

def teardown_project_delete():
    user = User()
    user.login('test_user_delete_api_project','test_pass')
    project = Project()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':ObjectId(user.user.id)})
    project.find('project 1')
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project 1'})
    model.conn.drop_database('project_1')

@with_setup(setup_project_delete,teardown_project_delete)
def test_project_delete():
    # login user get token
    user = User()
    user.login('test_user_delete_api_project','test_pass')
    
    api_key = user.user.auth_token
    print api_key
    project = Project()
    project.find('project 1')
    project_id = project.get_id()
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
    assert project_id not in test_user.user.project

    

def setup_user_project():
    # now create user
    user = User()
    user.create('test_user_update_project','test_pass','test@example.com') 
    # create project
    project = Project()
    project.create('project update','project update content')
    # associate project
    user.add_project(project.get_id())

def teardown_user_project():
    user = User()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'username':'test_user_update_project'})
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project update'})
    model.conn.drop_database('project_update')
    
@with_setup(setup_user_project,teardown_user_project)
def test_project_update():
    user = User()
    user.login('test_user_update_project','test_pass')
    api_key = user.user.auth_token
    project = Project()
    project.find('project update')
    test_client = webapp.app.test_client()
    url = '/api/project/%s/?api_key=%s' % (project.project.id,api_key)
    data = json.dumps({'description':'project updated content'})
    result = test_client.put(url,data=data,content_type='application/json')
    status = json.loads(result.data)
    print status
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
    user.add_project(project.get_id())
    project = Project()
    project.create('project list 2','project content 2')
    user.add_project(project.get_id())
    project = Project()
    project.create('project list 3','project content 3')
    user.add_project(project.get_id())

def teardown_user_project_list():
    user = User()
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'username':'test_user_list'})
    project = Project()
    model = MongoModel(project=project.project_,collection=project.collection_)
    model.delete({'name':'project list 1'})
    model.conn.drop_database('project_list_1')
    model.delete({'name':'project list 2'})
    model.conn.drop_database('project_list_2')
    model.delete({'name':'project list 3'})
    model.conn.drop_database('project_list_3')

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
    assert str(project.get_id()) in user.user.project

@with_setup(setup_user_project_list,teardown_user_project_list)
def test_user_project_withdraw():
    user = User()
    user.login('test_user_list','test_pass') 
    project = Project()
    project.find('project list 3')

    user.add_project(project.get_id())
    api_key = user.user.auth_token
    test_client = webapp.app.test_client()

    url = '/api/project/%s/?api_key=%s' % (project.get_id(),api_key)
       
    data = {'project':'project_list_3','action':'withdraw'}

    result = test_client.put(url,data=json.dumps(data),content_type='application/json')
    print result.data 
    user.login('test_user_list','test_pass')
    print user.user.project
    print project.get_id()
    print project.project.name
    assert not str(project.get_id()) in user.user.project



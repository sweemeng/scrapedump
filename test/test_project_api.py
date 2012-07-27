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
    print result.data
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
def test_project_create():
    # login user get token
    
    # do a post
    
    # now check project in user
    pass

def test_project_delete():
    # login user get token
    
    # do a delete
    
    # now check user don't exist
    pass

def setup_user_project():
    # now create user
    
    # create project

    # associate project
    
    pass

def teardown_user_project():
    pass

# Now need to create user and project at the same time
def test_project_update():
    pass

# now project created, you join or withdraw
# you are talking about user info, so go figure
def test_user_project_list():
    pass

def test_user_project_join():
    pass

def test_user_project_withdraw():
    pass



import webapp
from mongomodel.model import MongoModel
from project.model import Project
from user.model import User

from nose.tools import with_setup
import json
import bson.objectid as objectid


# this is a short test, but first, we need to bind project this to test now.

def setup_test_get():
    project = Project()
    project.create('scraped','test scraping')
    entry_id = project.add_entry('entry','test entry','entry','entry')
    model =  project.get_entry_collection(entry_id)
    model.insert({'a':1})

def teardown_test_get():
    model = MongoModel(project='scraped',collection='entry')
    model.delete({'a':1})
    model = MongoModel(project='internal',collection='project')
    model.delete({'name':'scraped'})

def setup_user():
    user = User()
    user.create('test_user','test_pass','test@example.com')
    project = Project()
    project.create('scraped','scraped')
    project.add_entry('entry','entry','localhost')
    user.add_project(project.get_id())

def teardown_user():
    user = User()
    user.login('test_user','test_pass')
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':objectid.ObjectId(str(user.user.id))})
    model = MongoModel(project='internal',collection='project')
    model.delete({'name':'scraped'})


@with_setup(setup_test_get,teardown_test_get)
def test_get_all():
    project = Project()
    project.find('scraped')
    entry_id = project.find_entry('entry')
    client = webapp.app.test_client()
    response = client.get('/api/db/%s/%s/' % (project.project.id,entry_id))
    result = json.loads(response.data)
    
    assert result[0]['a'] == 1

@with_setup(setup_test_get,teardown_test_get)
def test_get():
    mongo = MongoModel(project='scraped',collection='entry')
    client = webapp.app.test_client()

    data = mongo.all()

    id = str(data[0]['_id'])
    project = Project()
    project.find('scraped')
    entry_id = project.find_entry('entry')
    response = client.get('/api/db/%s/%s/%s/' % (project.project.id,entry_id,id))
    result = json.loads(response.data)

    assert result['a'] == 1

@with_setup(setup_user,teardown_user)
def test_insert():
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.auth_token
    client = webapp.app.test_client()
    data = {'a':1}
    project = Project()
    project.find('scraped')
    entry_id = project.find_entry('entry')
    url = '/api/db/%s/%s/?api_key=%s' % (project.project.id,entry_id,api_key)
    response = client.post(url,data=json.dumps(data),
            content_type='application/json')
    
    status = json.loads(response.data)
    assert status['status']

    mongo = MongoModel(project='scraped',collection='entry')
    check = mongo.all()
    assert check[0]['a'] == 1

    mongo.delete(check[0])

def setup_test_update():
    mongo = MongoModel(project='test_api_update',collection='test_api_entry')
    mongo.insert({'a':1})
    user = User()
    user.create('test_user_api_update','test_pass','test@example.com')
    project = Project()
    project.create('test api update','scraped')
    project.add_entry('test api entry','entry','localhost')
    user.add_project(project.get_id())


def teardown_test_update():
    mongo = MongoModel(project='test_api_update',collection='test_api_entry')
    mongo.delete({'a':2})
    user = User()
    user.login('test_user_api_update','test_pass')
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':objectid.ObjectId(str(user.user.id))})
    model = MongoModel(project='internal',collection='project')
    model.delete({'name':'test api update'})


@with_setup(setup_test_update,teardown_test_update)
def test_update():
    user = User()
    user.login('test_user_api_update','test_pass')
    api_key = user.user.auth_token

    project = Project()
    project.find('test api update')
    entry_id = project.find_entry('test api entry')
    print user.get_project()
    print project.get_id()
    mongo = MongoModel(project='test_api_update',collection='test_api_entry')
    data = mongo.query({'a':1})
    print data
    id = str(data['_id'])
    updated = {'a':2}
    url = '/api/db/%s/%s/%s/?api_key=%s' % (project.project.id,entry_id,id,api_key) 
    
    client = webapp.app.test_client()
    response = client.put(url, data = json.dumps(updated),
            content_type='application/json')
    print response.data
    status = json.loads(response.data)
    
    assert status['status']
  
    updated_data = mongo.query({'_id':objectid.ObjectId(id)})
    assert updated_data['a'] == 2

@with_setup(setup_user,teardown_user)
def test_delete():
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.auth_token
    mongo = MongoModel(project='scraped',collection='entry')
    client = webapp.app.test_client()

    mongo.insert({'a':1})
    
    data = mongo.query({'a':1})
    id = str(data['_id'])
    project = Project()
    project.find('scraped')
    entry_id = project.find_entry('entry')
    url = '/api/db/%s/%s/%s/?api_key=%s' % (project.project.id,entry_id,id,api_key) 
    response = client.delete(url)

    status = json.loads(response.data)
    assert status['status']
    
    check = mongo.query({'_id':objectid.ObjectId(id)})
    assert not check


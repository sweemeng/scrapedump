import webapp
from mongomodel.model import MongoModel
from user.model import User

from nose.tools import with_setup
import json
import bson.objectid as objectid



def setup_test_get():
    model =  MongoModel(project='scraped',collection='entry')
    model.insert({'a':1})

def teardown_test_get():
    model = MongoModel(project='scraped',collection='entry')
    model.delete({'a':1})

def setup_user():
    user = User()
    user.create('test_user','test_pass','test@example.com')

def teardown_user():
    user = User()
    user.login('test_user','test_pass')
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':objectid.ObjectId(str(user.user.id))})

@with_setup(setup_test_get,teardown_test_get)
def test_get_all():
    client = webapp.app.test_client()
    response = client.get('/api/scraped/entry/')
    result = json.loads(response.data)
    
    assert result[0]['a'] == 1

@with_setup(setup_test_get,teardown_test_get)
def test_get():
    mongo = MongoModel(project='scraped',collection='entry')
    client = webapp.app.test_client()

    data = mongo.all()
    id = str(data[0]['_id'])
    response = client.get('/api/scraped/entry/%s/' % (id))
    result = json.loads(response.data)

    assert result['a'] == 1

@with_setup(setup_user,teardown_user)
def test_insert():
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.api_key
    client = webapp.app.test_client()
    data = {'a':1}

    url = '/api/scraped/entry/?api_key=%s' % api_key
    response = client.post(url,data=json.dumps(data),
            content_type='application/json')
    
    status = json.loads(response.data)
    assert status['status']

    mongo = MongoModel(project='scraped',collection='entry')
    check = mongo.all()
    assert check[0]['a'] == 1

    mongo.delete(check[0])

def setup_test_update():
    mongo = MongoModel(project='scraped',collection='entry')
    mongo.insert({'a':1})
    user = User()
    user.create('test_user','test_pass','test@example.com')


def teardown_test_update():
    mongo = MongoModel(project='scraped',collection='entry')
    mongo.delete({'a':2})
    user = User()
    user.login('test_user','test_pass')
    model = MongoModel(project=user.project,collection=user.collection)
    model.delete({'_id':objectid.ObjectId(str(user.user.id))})


@with_setup(setup_test_update,teardown_test_update)
def test_update():
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.api_key
    
    mongo = MongoModel(project='scraped',collection='entry')
    data = mongo.query({'a':1})
    id = str(data['_id'])
    updated = {'a':2}
    url = '/api/scraped/entry/%s/?api_key=%s' % (id,api_key) 
    
    client = webapp.app.test_client()
    response = client.put(url, data = json.dumps(updated),
            content_type='application/json')

    status = json.loads(response.data)

    assert status['status']
    updated_data = mongo.query({'_id':objectid.ObjectId(id)})
    assert updated_data['a'] == 2

@with_setup(setup_user,teardown_user)
def test_delete():
    user = User()
    user.login('test_user','test_pass')
    api_key = user.user.api_key

    mongo = MongoModel(project='scraped',collection='entry')
    client = webapp.app.test_client()

    mongo.insert({'a':1})

    data = mongo.query({'a':1})
    id = str(data['_id'])
    url = '/api/scraped/entry/%s/?api_key=%s' % (id,api_key) 
    response = client.delete(url)

    status = json.loads(response.data)
    assert status['status']
    
    check = mongo.query({'_id':objectid.ObjectId(id)})
    assert not check


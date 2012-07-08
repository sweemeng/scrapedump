import webapp
from mongomodel.model import MongoModel
from nose.tools import with_setup
import json
import bson.objectid as objectid



def setup_test_get():
    model =  MongoModel()
    model.insert({'a':1})

def teardown_test_get():
    model = MongoModel()
    model.delete({'a':1})

@with_setup(setup_test_get,teardown_test_get)
def test_get_all():
    client = webapp.app.test_client()
    response = client.get('/api/')
    result = json.loads(response.data)
    
    assert result[0]['a'] == 1

@with_setup(setup_test_get,teardown_test_get)
def test_get():
    mongo = MongoModel()
    client = webapp.app.test_client()

    data = mongo.all()
    id = str(data[0]['_id'])
    response = client.get('/api/%s/' % (id))
    result = json.loads(response.data)

    assert result['a'] == 1

def test_insert():
    client = webapp.app.test_client()
    data = {'a':1}
    response = client.post('/api/',data=json.dumps(data),
            content_type='application/json')
    
    status = json.loads(response.data)
    assert status['status']

    mongo = MongoModel()
    check = mongo.all()
    assert check[0]['a'] == 1

    mongo.delete(check[0])

def setup_test_update():
    mongo = MongoModel()
    mongo.insert({'a':1})

def teardown_test_update():
    mongo = MongoModel()
    mongo.delete({'a':2})

@with_setup(setup_test_update,teardown_test_update)
def test_update():
    mongo = MongoModel()
    data = mongo.get({'a':1})
    id = str(data['_id'])
    updated = {'a':2}
    client = webapp.app.test_client()
    response = client.put('/api/%s' % id, data = json.dumps(updated),
            content_type='application/json')

    status = json.loads(response.data)

    assert status['status'] == True
    updated_data = mongo.get({'_id':objectid.ObjectId(id)})
    assert updated_data['a'] == 2
    

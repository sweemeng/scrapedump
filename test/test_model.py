from mongomodel.model import MongoModel
import pymongo

from nose.tools import with_setup


def setup_test_get_single():
    conn = pymongo.Connection()
    db = conn['scraped']
    entries = db['default']
    entries.insert({'a':1})

def teardown_test_get_single():
    conn = pymongo.Connection()
    db = conn['scraped']
    entries = db['default']
    entries.remove({'a':1})

@with_setup(setup_test_get_single,teardown_test_get_single)
def test_get_single():
    model = MongoModel()
    data = model.query({'a':1})
    assert data['a'] == 1

def setup_test_get_multiple():
    conn = pymongo.Connection()
    db = conn['scraped']
    entries = db['default']
    entries.insert({'a':1,'type':'test'})
    entries.insert({'b':2,'type':'test'})
    entries.insert({'c':3,'type':'test'})

def teardown_test_get_multiple():
    conn = pymongo.Connection()
    db = conn['scraped']
    entries = db['default']
    entries.remove({'type':'test'})

@with_setup(setup_test_get_multiple,teardown_test_get_multiple)
def test_get_multiple():
    model = MongoModel()
    data = model.query({'type':'test'},fetch_all=True)
    
    assert data[0]['a'] == 1
    assert data[1]['b'] == 2
    assert data[2]['c'] == 3

@with_setup(setup_test_get_multiple,teardown_test_get_multiple)
def test_get_all():
    model = MongoModel()
    data = model.all()
    assert data[0]['a'] == 1
    assert data[1]['b'] == 2
    assert data[2]['c'] == 3

def test_insert_remove():
    model = MongoModel()
    model.insert({'a':1,'b':2})
    data = model.query({'a':1})
    assert data['b'] == 2
    model.delete({'a':1})
    data = model.query({'a':1})
    assert not data

def setup_test_update():
    model = MongoModel()
    model.insert({'a':1,'b':2})

def teardown_test_update():
    model = MongoModel()
    model.delete({'a':1})

@with_setup(setup_test_update,teardown_test_update)
def test_update():
    model = MongoModel()
    model.update({'a':1},{'b':3})
    data = model.query({'a':1})
    assert data['b'] == 3

@with_setup(setup_test_update,teardown_test_update)
def test_update_add():
    model = MongoModel()
    model.update({'a':1},{'c':3})
    data = model.query({'a':1})
    print data
    assert 'c' in data
    assert data['c'] == 3
    

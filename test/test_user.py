from user import model
from mongomodel.model import MongoModel 
from nose.tools import with_setup
import bcrypt
from flask.ext.login import login_user
import hashlib


def test_empty_user():
    user = model.UserTemplate()
    assert hasattr(user,'id')
    assert hasattr(user,'username')
    assert hasattr(user,'password')
    assert hasattr(user,'api_key')
    assert hasattr(user,'project')
    assert hasattr(user,'active')
    assert hasattr(user,'auth_token')
    
    test_data = user.to_mongo()
    assert test_data.has_key('username')
    assert test_data.has_key('password')
    assert test_data.has_key('api_key')
    assert test_data.has_key('project') 
    assert test_data.has_key('active')
    assert test_data.has_key('auth_token')

def test_create_user():
    user = model.User()
    test_username = 'test_user'
    test_password = 'test_password'
    
    user.create(test_username,test_password)

    passwd = user.user.password

    assert user.user.username == test_username

    assert bcrypt.hashpw(test_password,passwd) == passwd
    
    auth_token = hashlib.sha224('%s%s' % (test_username,passwd))
    print auth_token.hexdigest()
    print user.user.auth_token
    assert user.user.auth_token == auth_token.hexdigest()
    
    db = MongoModel(project='internal',collection='user')
    
    test_result = db.query({'username':test_username}) 
    
    assert test_result['username'] == test_username
    assert bcrypt.hashpw(test_password,test_result['password']) == test_result['password'] 
    assert test_result['auth_token'] == auth_token.hexdigest()

    db.delete({'username':test_username})

def setup_test_login():
    user = model.User()
    user.create("test_user","test_password") 

def teardown_test_login():
    db = MongoModel(project='internal',collection='user')
    db.delete({'username':'test_user'})

@with_setup(setup_test_login,teardown_test_login)
def test_login_user():
    user = model.User()
    result = user.login('test_user','test_password')
    assert result.user.username == 'test_user'
    assert bcrypt.hashpw('test_password',result.user.password) == result.user.password 
    assert result.is_active() 

def test_empty_user():
    user = model.User()
    result = user.login('test_user','test_password')
    assert not result.user.username
    assert not result.user.id
    assert not result.is_active()


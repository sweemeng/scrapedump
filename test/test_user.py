from user import model
from mongomodel.model import MongoModel 
from nose.tools import with_setup
import bcrypt

def test_empty_user():
    user = model.UserTemplate()
    assert hasattr(user,'id')
    assert hasattr(user,'username')
    assert hasattr(user,'password')
    assert hasattr(user,'api_key')
    assert hasattr(user,'project')
    assert hasattr(user,'active')
    
    test_data = user.to_mongo()
    assert test_data.has_key('username')
    assert test_data.has_key('password')
    assert test_data.has_key('api_key')
    assert test_data.has_key('project') 
    assert test_data.has_key('active')

def test_create_user():
    user = model.User()
    test_username = 'test_user'
    test_password = 'test_password'
    
    user.create(test_username,test_password)

    passwd = user.user.password

    assert user.user.username == test_username

    assert bcrypt.hashpw(test_password,passwd) == passwd
    
    db = MongoModel(project='internal',collection='user')
    
    test_result = db.query({'username':test_username}) 
    
    assert test_result['username'] == test_username
    assert bcrypt.hashpw(test_password,test_result['password']) == test_result['password'] 

    db.delete({'username':test_username})

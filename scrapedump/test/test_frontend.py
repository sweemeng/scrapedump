import webapp
from nose.tools import with_setup
from user.model import User 
from mongomodel.model import MongoModel

# create test for project view
def setup_login():
    user = User()
    user.create('test_user','test_password','test@example.com')

def teardown_login():
    user = User()
    user.login('test_user','test_password')
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'_id':user.user.id})

@with_setup(setup_login,teardown_login)
def test_login():
    test_client = webapp.app.test_client()
    result = test_client.post('/login/',data={
        'username':'test_user',
        'password':'test_password'
    },follow_redirects=True)
    assert 'test_user' in result.data
    
    result = test_client.get('/logout/',follow_redirects=True)
    print result.data 
    assert 'Annonymous' in result.data

def test_main_page():
    test_client = webapp.app.test_client()
    result = test_client.get('/')
    assert 'Annonymous' in result.data

@with_setup(setup_login,teardown_login)
def test_user_settings_password():
    test_client = webapp.app.test_client()
    user = User()
    username = 'test_user'
    password = 'test_password'
    user.login(username,password)
    
    result = test_client.post('/login/',data={
        'username':username,
        'password':password
    },follow_redirects=True)
    
    result = test_client.get('/settings/',follow_redirects=True)
    assert user.user.auth_token in result.data

    # create an update call, then check data
    # remember to reauthenticate 
    
    password = 'test_pass'
    result = test_client.post('/settings/',data={
        'password':password,
        'confirm':password
    },follow_redirects=True)

    user = User()    
    user.login(username,password)
    
    assert user.is_authenticated()
    assert user.user.auth_token in result.data

def setup_user_settings_email():
    user = User()
    user.create('test_user_email','test_password','test@example.com')

def teardown_user_settings_email():
    user = User()
    user.login('test_user_email','test_password')

    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'username':'test_user_email'})
     
@with_setup(setup_user_settings_email,teardown_user_settings_email)
def test_user_settings_email():
    test_client = webapp.app.test_client()
    
    user = User()
    username = 'test_user_email'
    password = 'test_password'
    user.login(username,password)

    result = test_client.post('/login/',data={
        'username':username,
        'password':password
    },follow_redirects=True)
    result = test_client.get('/settings/',follow_redirects=True)
    assert user.user.email in result.data

    # create an update call, then check data
    # remember to reauthenticate 
    
    result = test_client.post('/settings/',data={
        'email':'tester@example.com'
    },follow_redirects=True)

    user = User()    
    user.login(username,password)
    
    assert user.user.email == 'tester@example.com'
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'_id':user.user.id})

def setup_register():
    pass

def teardown_register():
    user = User()
    user.login('test_register','test_password')
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'username':'test_register'})

@with_setup(setup_register,teardown_register)
def test_user_registration():
    username = 'test_register'
    password = 'test_password'
    email = 'test@example.com'

    test_client = webapp.app.test_client()
    create = test_client.post('/register/',data={
        'username':username,
        'password':password,
        'confirm':password,
        'email':email    
    },follow_redirects=True)
    
    user = User()
    user.login(username,password)
    assert user.is_authenticated()
    
 
    
    

import webapp
from nose.tools import with_setup
from user.model import User 
from mongomodel.model import MongoModel

def setup_test_login():
    user = User()
    user.create('test_user','test_password')

def teardown_test_login():
    user = User()
    user.login('test_user','test_password')
    db = MongoModel(project=user.project,collection=user.collection)
    db.delete({'_id':user.user.id})

@with_setup(setup_test_login,teardown_test_login)
def test_login():
    test_client = webapp.app.test_client()
    result = test_client.post('/login/',data={
        'username':'test_user',
        'password':'test_password'
    },follow_redirects=True)
    assert 'user is logged in' in result.data

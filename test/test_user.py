from user import model

def test_empty_user():
    user = model.UserTemplate()
    assert hasattr(user,'username')
    assert hasattr(user,'password')
    assert hasattr(user,'api_key')
    assert hasattr(user,'project')
    
    test_data = user.to_mongo()
    assert test_data.has_key('username')
    assert test_data.has_key('password')
    assert test_data.has_key('api_key')
    assert test_data.has_key('project') 

def test_create_user():
    pass

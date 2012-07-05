from event.event import Event

def test_create_with_param():
    event = Event('create',{'a':1},{'b':2})

    test_dict = event.to_dict()
    
    assert test_dict['action'] == 'create'
    assert test_dict['data'] == {'a':1}
    assert test_dict['param'] == {'b':2}


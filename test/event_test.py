from event.event import Event
import json

def test_create_with_param():
    def dict_checker(test_dict):
        assert test_dict['action'] == 'create'
        assert test_dict['data'] == {'a':1}
        assert test_dict['param'] == {'b':2}

    event = Event('create',{'a':1},{'b':2})

    test_dict = event.to_dict()
    
    dict_checker(test_dict)

    test_json = event.to_json()

    test_dict = json.loads(test_json)
    dict_checker(test_dict)
    

def test_create_from_dict():
    event =  Event()
    test_dict = {
            'action':'create',
            'data':{'a':1},
            'param':{'b':2}
            }
    event.from_dict(test_dict)

    assert event.action == 'create'
    assert event.data['a'] == 1
    assert event.param['b'] == 2

def test_create_from_json():
    event =  Event()
    test_dict = {
            'action':'create',
            'data':{'a':1},
            'param':{'b':2}
            }
    event.from_json(json.dumps(test_dict))

    assert event.action == 'create'
    assert event.data['a'] == 1
    assert event.param['b'] == 2






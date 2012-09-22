from utils.file_handler import JsonHandler
from utils.file_handler import CSVHandler
import cStringIO
import json


def test_json_handler_list():
    data = json.dumps([{'a':1,'b':2},{'a':3,'b':4}])
    json_file = cStringIO.StringIO(data)
    handler = JsonHandler(json_file)
    test_run = handler.run()
    
    result = test_run.next()
    assert result['a'] == 1
    assert result['b'] == 2
    
    result = test_run.next()
    assert result['a'] == 3
    assert result['b'] == 4

def test_json_handler_dict():
    data = json.dumps({'a':1,'b':2})
    json_file = cStringIO.StringIO(data)
    handler = JsonHandler(json_file)
    test_run = handler.run() 
    
    result = test_run.next()
    assert result['a'] == 1
    assert result['b'] == 2

def test_csv_handler():
    data = "a,b,c\n1,2,3\n4,5,6"
    csv_file = cStringIO.StringIO(data)
    handler = CSVHandler(csv_file)
    test_run = handler.run()
    result = test_run.next()
    print result
    assert result['a'] == '1'
    assert result['b'] == '2'
    assert result['c'] == '3'
    result = test_run.next()
    assert result['a'] == '4'
    assert result['b'] == '5'
    assert result['c'] == '6'

def test_tsv_handler():
    data = "a\tb\tc\n1\t2\t3\n4\t5\t6"
    csv_file = cStringIO.StringIO(data)
    handler = CSVHandler(csv_file)
    test_run = handler.run()
    result = test_run.next()
    print result
    assert result['a'] == '1'
    assert result['b'] == '2'
    assert result['c'] == '3'
    result = test_run.next()
    assert result['a'] == '4'
    assert result['b'] == '5'
    assert result['c'] == '6'


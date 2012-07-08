from flask import Flask
from dummy.action import DummyApi
from api.actions import DataApi

app = Flask(__name__)

api_views = DataApi.as_view('api')

app.add_url_rule('/dummy/',view_func=DummyApi.as_view('dummy'))
app.add_url_rule('/api/',defaults={'entry_id':None},
        view_func=api_views,methods=['GET',])
app.add_url_rule('/api/',view_func=api_views,methods=['POST',])
app.add_url_rule('/api/<entry_id>/',
        view_func=api_views,methods=['GET','PUT',])

if __name__ == '__main__':
    app.run()

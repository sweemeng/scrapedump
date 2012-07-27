from flask.views import MethodView
from flask import jsonify

from mongomodel.model import MongoModel
from user.model import User
import  bson
import bson.objectid as objectid
import bson.json_util
from flask import json
from flask import request
from flask import Response


class DataApi(MethodView):
    def get(self,project,entry,entry_id):
        model = MongoModel(project=project,collection=entry)
        if entry_id:
            id = objectid.ObjectId(str(entry_id))
            result = model.query({'_id':id})
        else:
            result = model.all()
        
        data = json.dumps(result,default=bson.json_util.default)
        resp = Response(data,status=200,mimetype='application/json')
        resp.headers['Link'] = 'http://localhost:5000'
        return resp

    def post(self,project,entry):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})

        if project not in user.user.project:
            return jsonify({'status':False})

        model = MongoModel(project=project,collection=entry)
        model.insert(request.json)
        return jsonify({'status':True})

    def put(self,project,entry,entry_id):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})

        if project not in user.user.project:
            return jsonify({'status':False})

        id = objectid.ObjectId(str(entry_id))
        model = MongoModel(project=project,collection=entry)

        model.update({'_id':id},request.json)
        
        return jsonify({'status':True})

    def delete(self,project,entry,entry_id):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})
        if project not in user.user.project:
            return jsonify({'status':False})

        id = objectid.ObjectId(str(entry_id))
        model = MongoModel(project=project,collection=entry)
        model.delete({'_id':id})
        
        return jsonify({'status':True})



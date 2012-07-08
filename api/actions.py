from flask.views import MethodView
from flask import jsonify

from mongomodel.model import MongoModel
import  bson
import bson.objectid as objectid
import bson.json_util
from flask import json
from flask import request
from flask import Response


class DataApi(MethodView):
    def get(self,entry_id):
        model = MongoModel()
        if entry_id:
            id = objectid.ObjectId(str(entry_id))
            result = model.query({'_id':id})
        else:
            result = model.all()
        
        data = json.dumps(result,default=bson.json_util.default)
        resp = Response(data,status=200,mimetype='application/json')
        resp.headers['Link'] = 'http://localhost:5000'
        return resp

    def post(self):
        model = MongoModel()
        model.insert(request.json)
        return jsonify({'status':True})

    def put(self,entry_id):
        id = objectid.ObjectId(str(entry_id))
        model = MongoModel()

        model.update({'_id':id},request.json)
        
        return jsonify({'status':True})

    def delete(self,entry_id):
        id = objectid.ObjectId(str(entry_id))
        model = MongoModel()
        model.delete({'_id':id})
        
        return jsonify({'status':True})



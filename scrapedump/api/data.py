from flask.views import MethodView
from flask import jsonify
from flask.ext.principal import Identity

from mongomodel.model import MongoModel
from user.model import User
from user.permission import EditProjectPermission
from user.permission import edit_project_need
from project.model import Project
from utils.authorization import authorized
import  bson
import bson.objectid as objectid
import bson.json_util
from flask import json
from flask import request
from flask import Response
from flask import abort


# Now integrate with project, now it should be project_id, entry_id, not name. 
class DataApi(MethodView):
    def get(self,project_id,entry,entry_id):
        project = Project()
        project.get(project_id)
        model = project.get_entry_collection(entry)
        if entry_id:
            id = objectid.ObjectId(str(entry_id))
            result = model.query({'_id':id})
        else:
            result = model.all()
        
        data = json.dumps(result,default=bson.json_util.default)
        resp = Response(data,status=200,mimetype='application/json')
        resp.headers['Link'] = 'http://localhost:5000'
        return resp

    def post(self,project_id,entry):
        api_key = request.args.get('api_key')
        
        if not authorized(api_key,project_id):
            return jsonify({'status':False,'message':'user is not authenticated'})
        
        # Lets disable it for now. Until flask-principal is implemented
        #if project not in user.user.project:
        #    return jsonify({'status':False,'message':'user don nott have access to project'})
        
        project = Project()
        project.get(project_id)
        model = project.get_entry_collection(entry)

        model.insert(request.json)
        project.entry_updated() 
        return jsonify({'status':True})

    def put(self,project_id,entry,entry_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})

        #if project not in user.user.project:
        #    return jsonify({'status':False})

        id = objectid.ObjectId(str(entry_id))

        project = Project()
        project.get(project_id)
        model = project.get_entry_collection(entry)

        model.update({'_id':id},request.json)
        project.entry_updated() 
        return jsonify({'status':True})

    def delete(self,project_id,entry,entry_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})

        #if project not in user.user.project:
        #    return jsonify({'status':False})

        id = objectid.ObjectId(str(entry_id))

        project = Project()
        project.get(project_id)
        model = project.get_entry_collection(entry)
        model.delete({'_id':id})
        project.entry_updated() 
        return jsonify({'status':True})



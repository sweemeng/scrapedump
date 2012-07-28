from flask.views import MethodView
from flask import jsonify

from projectmodel.model import Project
from projectmodel.model import ProjectList
from mongomodel.model import MongoModel
from user.model import User
import bson
import bson.objectid as objectid
import bson.json_util
from flask import json
from flask import request
from flask import Response


class ProjectApi(MethodView):
    def get(self,project_id):
        if project_id:
            project = Project()
            project.get(project_id)
            data = project.project.to_mongo()
        else:
            project = ProjectList()
            data = []
            for p in project.all():
                data.append(p.project.to_mongo())
        
        data = json.dumps(data,default=bson.json_util.default)
        resp = Response(data,status=200,mimetype='application/json')
        resp.headers['Link'] = 'http://localhost:5000'
        return resp
    
    def post(self):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})

        data = request.json
        project = Project()
        project.create(data['name'],data['description'])
        user.add_project(project.project.name_to_mongo())
        return jsonify({'status':True})
    
    def put(self,project_id):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        
        if not project.project.name_to_mongo() in user.user.project:
            return jsonify({'status':False})
        
        data = request.json
        project.project.description = data['description']
        project.save()
        return jsonify({'status':True})
    
    def delete(self,project_id):
        api_key = request.args.get('api_key')
        user = User()
        user.api_login(api_key)
        if not user.is_authenticated():
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        if not project.project.name_to_mongo() in user.user.project:
            return jsonify({'status':False})
        user.remove_project(project.project.name_to_mongo())
        model = MongoModel(project=project.project_,collection=project.collection_)
        model.delete({'_id':objectid.ObjectId(str(project_id))})
        
        return jsonify({'status':True})



from flask.views import MethodView
from flask import jsonify

from model import Project
from model import ProjectList
from mongomodel.model import MongoModel
from user.model import User
from utils.authorization import authorized
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
            data = {}
            project = ProjectList()
            all_project = []
            for p in project.all():
                print p.project.to_mongo()
                all_project.append(p.project.to_mongo())
            data['all'] = all_project
                
            if request.args.get('api_key'):
                user = User()
                user.api_login(request.args.get('api_key'))
                user_project = user.user.project
                data['user'] = self.get_project(user_project)
            
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
        user.add_project(str(project.get_id()))
        return jsonify({'status':True})
    
    def put(self,project_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        
        data = request.json
        
        if data.get('action') == 'join':
            user.add_project(project.project.name_to_mongo())
            return jsonify({'status':True})
        elif data.get('action') == 'withdraw':
            user.remove_project(project.project.name_to_mongo())
            return jsonify({'status':True})
            
        if not project.project.name_to_mongo() in user.user.project:
            return jsonify({'status':False})
        
        project.project.description = data['description']
        project.save()
        return jsonify({'status':True})
    
    def delete(self,project_id):
        api_key = request.args.get('api_key')
        if not authorized(project_id,api_key):
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        if not project.project.name_to_mongo() in user.user.project:
            return jsonify({'status':False})
        user.remove_project(project.project.name_to_mongo())
        model = MongoModel(project=project.project_,collection=project.collection_)
        model.delete({'_id':objectid.ObjectId(str(project_id))})
        
        return jsonify({'status':True})
    
    def get_project(self,name):
        name = [i.replace('_',' ') for i in  name]
        
        temp = []
        
        for n in name:
            project = Project()
            project.find(n)
            temp.append(project.project.to_mongo())
        return temp



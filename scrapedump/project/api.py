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
        project = Project()
        project.get(project_id)
        user = User()
        user.api_login(api_key)
        data = request.json
                
        if data.get('action') == 'join':
            user.add_project(project.get_id())
            return jsonify({'status':True,'msg':'join project'})
        elif data.get('action') == 'withdraw':
            user.remove_project(project.get_id())
            return jsonify({'status':True,'msg':'withdrawn from project'})
            
        if not authorized(api_key,project_id):
            return jsonify({'status':False,'msg':'unauthorized'})

        if not project.get_id() in user.user.project:
            return jsonify({'status':False,'msg':'project not in user'})
        
        project.project.description = data['description']
        project.save()
        return jsonify({'status':True})
    
    def delete(self,project_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})
        user = User()
        user.api_login(api_key)
        project = Project()
        project.get(project_id)
        if not project.get_id() in user.user.project:
            return jsonify({'status':False})
        user.remove_project(project.get_id())
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


class EntryApi(MethodView):
    def get(self,project_id,entry_id):
        project = Project()
        project.get(project_id)
        data = project.get_entry(entry_id)
        data = json.dumps(data,default=bson.json_util.default)
        resp = Response(data,status=200,mimetype='application/json')
        resp.headers['Link'] = 'http://localhost:5000'
    
    def post(self,project_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})
        project = Project()
        project.get(project_id)
        data = request.json 
        project.add_entry(data['name'],data['description'],data['source'])
        return jsonify({'status':True,'msg':'entry created'})

    def put(self,project_id,entry_id):
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        data = request.json
        entry = project.project.entry[entry_id]
        entry['description'] = data['description']
        entry['source'] = data['source']
        project.save()
        return jsonify({'status':True,'msg':'entry updated'})
    
    def delete(self,project_id,entry_id):        
        api_key = request.args.get('api_key')
        if not authorized(api_key,project_id):
            return jsonify({'status':False})

        project = Project()
        project.get(project_id)
        del(project.project.entry[entry_id])
        del(project.project.stats[entry_id])
        del(project.project.export[entry_id])
        del(project.project.input_file[entry_id])
        project.save()

from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from flask import Response
from flask import jsonify
from flask import make_response
from flask import abort
from flask.ext.login import login_required
from flask.ext.login import current_user
from flask.ext.wtf import TextField

from user.model import User
from user.permission import EditProjectPermission
from forms.user import UserForm
from forms.user import UserUpdateForm
from forms.project import ProjectForm
from forms.project import ProjectUpdateForm
from project.model import Project
from project.model import ProjectList
from backend.data_loader import loader_task
from forms.entry import EntryForm
from forms.entry import EntryUpdateForm
import json


frontend = Blueprint('frontend',__name__,
                     template_folder='templates')

@frontend.route('/')
def index():
    if current_user.is_authenticated():
        username = current_user.user.username
    else:
        username = "Annonymous"
    projects = ProjectList()

    project_list = projects.list()
    return render_template("main_page.html",username=username,projects=project_list)

@frontend.route('/project/<project_id>/',methods=['POST','GET'])
def project_view(project_id):
    form = ProjectUpdateForm(csrf_enabled=False)
    project = Project()
    print project_id
    project.get(project_id)
    permission = EditProjectPermission(project_id) 
    edit = False
    if request.method == 'POST':
        edit = True
        if not permission.can():
            abort(403)
        if form.validate_on_submit():
            # name is not edited because it bind to the database name
            project.project.description = form.description.data
            project.save()

    return render_template('project_view.html',project=project,form=form,edit=edit,permission=permission)

@frontend.route('/project/',methods=['POST','GET'])
@login_required
def project_create():
    form = ProjectForm(csrf_enabled=False)
    print "processing form"
    if form.validate_on_submit():
        print 'form submitted'
        project = Project()
        project.create(form.name.data,form.description.data)
        user = current_user
        user.add_project(str(project.project.id))
        return redirect('/project/%s/'% project.project.id)
    
    return render_template('project_create.html',form=form)

@frontend.route('/entry/<project_id>/create/',methods=['GET','POST'])
def project_entry_create(project_id):
    form = EntryForm(csrf_enabled=False)
    edit = False
    project = Project()
    project.get(project_id)
    permission = EditProjectPermission(project_id)
    if not permission.can():
        abort(403)
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        source = form.source.data
        entry_id = project.add_entry(name,description,source)
        return redirect('/project/%s/' % (project_id))
        
    return render_template('entry_create.html',form=form)


@frontend.route('/entry/<project_id>/<entry_id>/',methods=['GET','POST'])
def project_entry_detail(project_id,entry_id):
    # add entry should be a new form, remove from old form
    permission = EditProjectPermission(project_id)
    form = EntryUpdateForm(csrf_enabled=False)
    # we also will need upload form FYI
    project = Project()
    project.get(project_id)
    edit = False
    print project.project.entry.keys()
    entry = project.get_entry(entry_id)
    if form.validate_on_submit():
        if not permission.can():
            abort(403)
        description = form.description.data
        source = form.source.data
        project.update_entry(entry_id,description,source)
        edit = True
    # not to mention we will need a project detail
    return render_template('entry_view.html',project=project,form=form,edit=edit,entry_id=entry_id,permission=permission)

@frontend.route('/upload/<project_id>/<entry_id>/',methods=['POST'])
@login_required
def load_data_upload(project_id,entry_id):
    # This should return json
    # look at jquery-upload
    print "getting upload"
    uploads = request.files.getlist('files[]')
    print "file length: %d" % len(uploads)
    project = Project()
    project.get(project_id)
    # project add_datafile should return file_id
    uploaded_all = []
    # first what if it is a invalid file, 
    # second what if it failed
    for uploaded in uploads:
        print 'filename being uploaded %s' % uploaded.filename
        try:
            file_id = project.add_datafile(entry_id,uploaded)
        except:
            data = {
                'filename':uploaded.filename,
                'name':uploaded.filename.replace('.','_'),
                'content-type':uploaded.content_type,
                'msg':'Invalid File Type, only CSV/Json are supported',
                'success':False
            }
            uploaded_all.append(data)
            continue
        try:
            task_id = loader_task.delay(project_id,entry_id,file_id)
    
            project.set_load_worker(entry_id,file_id,task_id.id)
        except:
            data = {
                'name':uploaded.filename.replace('.','_'),
                'filename':uploaded.filename,
                'content-type':uploaded.content_type,
                'msg':'Problem processing file',
                'success':False,
            }
            uploaded_all.append(data)
            continue

        test_file = project.get_datafile(file_id)

        get_url = '/download/%s/%s/' % (project_id,entry_id)
        delete_url = '/delete/%s/%s/' % (project_id,entry_id)
        data = {
            'success':True,
            'msg':'',
            'file_id':file_id,
            'length':test_file.length,
            'name':test_file.name.replace('.','_'),
            'filename':test_file.name,
            'content-type':test_file.content_type,
            'url':get_url,
            'delete':delete_url
        }
        uploaded_all.append(data)
    
    data = json.dumps(uploaded_all)
    resp = Response(data,status=200,mimetype='application/json')
    resp.headers['Link'] = 'http://localhost:5000'
    return resp


@frontend.route('/download/<project_id>/<entry_id>/<file_id>/',methods=['GET'])
def get_data_upload(project_id,entry_id,file_id):
    # this will allow download of the file. 
    project = Project()
    project.get(project_id)
    metadata = project.get_datafile_metadata(entry_id,file_id)
    response = make_response(project.get_datafile(file_id).read())
    response.headers['Content-Description'] = 'Uploaded File'
    response.headers['Content-Type'] = 'application/%s' % metadata['filename'].split('.')[-1]
    response.headers['Content-Length'] = metadata['size']
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % metadata['filename']
    return response 

@frontend.route('/delete/project_id/file_id/',methods=['POST'])
def delete_data_upload(project_id,entry_id,file_id):
    project = Project()
    project.get(project_id)
    try:
        project.delete_datafile(entry_id,file_id) 
        status = {'status':'Success','message':'completed'}
    except:
        status = {'status':'Failed','message':'error deleting file'}
        
    
    return jsonify([status])

@frontend.route('/settings/',methods=['POST','GET'])
@login_required
def settings():
    user = current_user.user
    form = UserUpdateForm(csrf_enabled=False,obj=user)
    if form.validate_on_submit():
        current_user.update(form.password.data,form.email.data)
        user = current_user.user
        
    form.populate_obj(user) 
    return render_template('settings.html',user=user,form=form)

@frontend.route('/register/',methods=['POST','GET'])
def register():
    user = User()
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        user.create(form.username.data,form.password.data,form.email.data)
        
    return render_template('register.html',form=form)

@frontend.route('/entry/<project_id>/<entry>/',methods=['POST','GET'])
def get_entry(project_id,entry):
    form = EntryUpdateForm()
    edit = False
    # entry should be short_name
    if form.validate_on_submit():
        project = Project()
        description = form.description.data
        source = form.source.data
        project.get(project_id)
        project.update_entry(entry,description,source)
        return redirect('/entry/%s/%s/' % (project_id,entry))
    project = Project()
    project.find(project_name)
    return render_template('entry_view.html',project=project,entry=entry,
                           edit=edit,form=form)

@frontend.route('/entry/<project_id>/',methods=['POST','GET'])
def add_entry(project_id):
    form = EntryForm(csrf_enabled=False)
    if form.validate_on_submit():
        project = Project()
        project.get(project_id)
        name = form.name.data
        description  = form.description.data
        short_name = form.description.data
        source = form.description.data
        project.add_entry(name,description,source)
        return redirect('/project/%s' % project_id)
    return render_template('entry_create.html',form=form)

@frontend.route('/export/<project_id>/<entry_id>/<export_type>/')
def download_export(project_id,entry_id,export_type):
    project = Project()
    project.get(project_id)
    metadata = project.get_exported_file(entry_id)
    file_ = project.get_datafile(str(metadata[export_type]))
    response = make_response(file_.read())
    response.headers['Content-Description'] = 'Uploaded File'
    response.headers['Content-Type'] = 'application/%s' % file_.content_type
    response.headers['Content-Length'] = file_.length
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_.filename
    return response 


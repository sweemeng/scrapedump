from flask import Blueprint
from flask import render_template
from flask import flash
from flask import redirect
from flask import request
from flask.ext.login import login_required
from flask.ext.login import current_user
from flask.ext.wtf import TextField

from user.model import User
from forms.user import UserForm
from forms.user import UserUpdateForm
from forms.project import ProjectForm
from forms.project import ProjectUpdateForm
from project.model import Project
from project.model import ProjectList
from backend.data_loader import loader_task
from forms.entry import EntryForm
from forms.entry import EntryUpdateForm

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
    edit = False
    if request.method == 'POST':
        edit = True
        if form.validate_on_submit():
            # name is not edited because it bind to the database name
            project.project.description = form.description.data
            project.save()

    return render_template('project_view.html',project=project,form=form,edit=edit)

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
        user.add_project(project.project.name_to_mongo())
        return redirect('/project/%s/'% project.project.id)
    
    return render_template('project_create.html',form=form)

@frontend.route('/project/<project_id>/entry/create/',methods=['GET','POST'])
def project_entry_create(project_id):
    form = EntryCreateForm(csrf_enabled=False)
    edit = False
    if form.validate_on_submit():
        pass
    return render_template('entry_view.html',project=project,entry=entry,edit=edit)


@frontend.route('/project/<project_id>/<entry_id>/',methods=['GET','POST'])
def project_entry_detail(project_id,entry_name):
    # add entry should be a new form, remove from old form
    form = EntryUpdateForm(csrf_enabled=False)
    # we also will need upload form FYI
    project = Project()
    project.find(project_id)
    stats = project.project.stats[entry_id]
    data_files = project.project.input_file[entry_id]
    # not to mention we will need a project detail
    return render_template('entry_detail.html',project=project,form=form,edit=edit)

@frontend.route('/project/upload/<project_id>/<entry_id>/',methods=['POST'])
@login_required
def load_data_upload(project_id,entry_name):
    uploaded = request.File['data_file']
    project = Project()
    project.get(project_id)
    # project load_datafile should return file_id
    file_id = project.load_datafile(uploaded)
    
    task_id = loader_task(project_name,entry_name,file_id)
    project.add_loadworker(task_id)
    # one more thing, jquery upload require json response
    # they will also need a view to get the file 
    return redirect('/project/%s/' % project_name)

@frontend.route('/project/download/<project_id>/<file_id>/',methods=['GET'])
def get_data_upload(project_id,entry_name,file_id):
    # this will allow download of the file. 
    project = Project()
    project.get(project_id)
    project.find(project_name.replace('_',' '))
    return response(project.get_datafile(file_id)) 

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

@frontend.route('/entry/<project_id>/<entry>',methods=['POST','GET'])
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
        pass
    project - Project()
    project.find(project_name)
    return render_template('entry_view.html',project=project,entry=entry,
                           edit=edit,form=form)

@frontend.route('/entry/<project_id>/',methods=['POST','GET'])
def add_entry(project_id):
    form = EntryForm(csrf_enabled=False)
    if form.validated_on_submit():
        project = Project()
        project.get(project_id)
        name = form.name.data
        description  = form.description.data
        short_name = form.description.data
        source = form.description.data
        project.add_entry(name,description,source,short_name=short_name)
    return render_template('entry_create.html',form=form)

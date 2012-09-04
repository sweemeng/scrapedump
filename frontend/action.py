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
from projectmodel.model import Project
from projectmodel.model import ProjectList


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

@frontend.route('/project/<project_name>/',methods=['POST','GET'])
def project_view(project_name):
    form = ProjectUpdateForm(csrf_enabled=False)
    project = Project()
    project.find(project_name.replace('_',' '))
    entries = project.project.entries
    edit = False
    if request.method == 'POST':
        edit = True
        if form.validate_on_submit():
            # name is not edited because it bind to the database name
            project.project.description = form.description.data
            project.save()
            project.add_entries(form.entry.data)
            entries = project.project.entries

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
        print form.entry
        project.add_entries(form.entry.data)
        user = current_user
        user.add_project(project.project.name_to_mongo())
        return redirect('/project/%s/'% project.to_mongo_name())
    
    return render_template('project_create.html',form=form)

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

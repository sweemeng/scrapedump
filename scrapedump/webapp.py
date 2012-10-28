from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask import current_app
from flask import session
from flask.ext.login import LoginManager
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import login_required
from flask.ext.login import current_user
from flask.ext.principal import identity_loaded
from flask.ext.principal import identity_changed
from flask.ext.principal import Principal
from flask.ext.principal import Identity
from flask.ext.principal import UserNeed
from flask.ext.principal import RoleNeed
from flask.ext.principal import AnonymousIdentity
from forms.login import LoginForm
from flask import flash

from api.data import DataApi
from project.api import ProjectApi
from project.api import EntryApi
from user.model import User
from user.permission import admin_permission
from user.permission import user_permission
from user.permission import edit_project_need
from user.permission import EditProjectPermission
from frontend.action import frontend


app = Flask(__name__)

app.config['SECRET_KEY'] = '1234567'

login_manager = LoginManager()

login_manager.setup_app(app)
principals = Principal(app)

login_manager.anonymous_user = User
@login_manager.user_loader
def load_user(userid):
    user = User()
    return user.get(userid)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender,identity):
    identity.user = current_user

    identity.provides.add(UserNeed(current_user.get_id()))

    for role in current_user.get_role():
        identity.provides.add(RoleNeed(role))
    
    for project in current_user.get_project():
        identity.provides.add(edit_project_need(project))

@frontend.route('/login/',methods=['GET','POST'])
def login():
    form = LoginForm(csrf_enabled=False)
    user = User()
    if form.validate_on_submit():
	username = form.username.data
        password = form.password.data
        user = user.login(username,password)
        login_user(user)
        flash('user is logged in')
        identity_changed.send(current_app._get_current_object(),identity=Identity(user.user.id))
        return redirect(request.args.get('next') or '/')
    return render_template('login.html',form=form)

@frontend.route('/logout/')
@login_required
def logout():
    for key in ('identity.name','identity.auth_type'):
        session.pop(key,None)
    logout_user()
    identity_changed.send(current_app._get_current_object(),identity=AnonymousIdentity())
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized():
    return "unauthorized"


api_views = DataApi.as_view('api')
project_api = ProjectApi.as_view('project')
entry_api = EntryApi.as_view('entry')

app.add_url_rule('/api/project/',defaults={'project_id':None},
        view_func=project_api,methods=['GET',])
app.add_url_rule('/api/project/',view_func=project_api,methods=['POST',])
app.add_url_rule('/api/project/<project_id>/',
        view_func=project_api,methods=['GET','PUT','DELETE',])

app.add_url_rule('/api/db/<project_id>/<entry>/',defaults={'entry_id':None},
        view_func=api_views,methods=['GET',])
app.add_url_rule('/api/db/<project_id>/<entry>/',view_func=api_views,methods=['POST',])
app.add_url_rule('/api/db/<project_id>/<entry>/<entry_id>/',
        view_func=api_views,methods=['GET','PUT','DELETE',])

app.add_url_rule('/api/entry/<project_id>/',defaults={'entry_id':None},
        view_func=entry_api,methods=['GET',])
app.add_url_rule('/api/entry/<project_id>/',view_func=entry_api,methods=['POST',])
app.add_url_rule('/api/entry/<project_id>/<entry_id>/',
        view_func=entry_api,methods=['GET','PUT','DELETE',])


app.register_blueprint(frontend,url_prefix='')


def run():
    app.debug = True
    app.run()

if __name__ == '__main__':
    print "BOOM"
    run()

from flask import Flask
from flask import redirect
from flask import request
from flask import render_template
from flask.ext.login import LoginManager
from flask.ext.login import login_user
from flask.ext.login import logout_user
from flask.ext.login import login_required
from forms.login import LoginForm
from flask import flash

from api.data import DataApi
from api.project import ProjectApi
from user.model import User
from frontend.action import frontend

app = Flask(__name__)

app.config['SECRET_KEY'] = '1234567'

login_manager = LoginManager()

login_manager.setup_app(app)

@login_manager.user_loader
def load_user(userid):
    user = User()
    return user.get(userid)

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
        return redirect(request.args.get('next') or '/')
    return render_template('login.html',form=form)

@frontend.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized():
    return "unauthorized"


api_views = DataApi.as_view('api')
project_api = ProjectApi.as_view('project')

app.add_url_rule('/api/project/',defaults={'project_id':None},
        view_func=project_api,methods=['GET',])
app.add_url_rule('/api/project/',view_func=project_api,methods=['POST',])
app.add_url_rule('/api/project/<project_id>/',
        view_func=project_api,methods=['GET','PUT','DELETE',])

app.add_url_rule('/api/db/<project>/<entry>/',defaults={'entry_id':None},
        view_func=api_views,methods=['GET',])
app.add_url_rule('/api/db/<project>/<entry>/',view_func=api_views,methods=['POST',])
app.add_url_rule('/api/db/<project>/<entry>/<entry_id>/',
        view_func=api_views,methods=['GET','PUT','DELETE',])


app.register_blueprint(frontend,url_prefix='')


if __name__ == '__main__':
    app.debug = True
    app.run()

from flask import Blueprint
from flask import render_template
from flask import flash
from flask.ext.login import login_required
from flask.ext.login import current_user

from user.model import User
from forms.user import UserForm
from forms.user import UserUpdateForm


frontend = Blueprint('frontend',__name__,
                     template_folder='templates')

@frontend.route('/')
def index():
    if current_user.is_authenticated():
        username = current_user.user.username
    else:
        username = "Annonymous"
    return render_template("main_page.html",username=username)

@frontend.route('/settings/',methods=['POST','GET'])
def settings():
    user = current_user.user
    form = UserUpdateForm(csrf_enabled=False,obj=user)
    if form.validate_on_submit():
        current_user.update(form.password.data)
        user = current_user.user
        
    form.populate_obj(user) 
    return render_template('settings.html',user=user,form=form)

@frontend.route('/register/',methods=['POST','GET'])
def register():
    user = User()
    form = UserForm(csrf_enabled=False)
    if form.validate_on_submit():
        user.create(form.username.data,form.password.data)
        
    return render_template('register.html',form=form)

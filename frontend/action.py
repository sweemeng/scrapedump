from flask import Blueprint
from flask import render_template
from flask import flash
from flask.ext.login import login_required
from flask.ext.login import current_user

from user.model import User


frontend = Blueprint('frontend',__name__,
                     template_folder='templates')

@frontend.route('/')
def index():
    if current_user.is_authenticated():
        username = current_user.user.username
    else:
        username = "Annonymous"
    return render_template("main_page.html",username=username)



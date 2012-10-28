from user.model import User
from flask.ext.principal import Identity
from flask.ext.principal import UserNeed
from flask.ext.principal import identity_loaded
from flask.ext.principal import identity_changed
from flask.ext.login import login_user
from flask import current_app
from flask import session
from user.permission import EditProjectPermission
from user.permission import edit_project_need


def authorized(api_key,project_id):
    user = User()
    print "api key is %s" % api_key
    user.api_login(api_key)
    if not user.is_authenticated():
        print "wrong password"
        return False
    login_user(user)
    identity_changed.send(current_app._get_current_object(),identity=Identity(user.user.id))
    
    permission = EditProjectPermission(project_id)
   
    if not permission.can():
        print "bad permission"
        return False
    return True


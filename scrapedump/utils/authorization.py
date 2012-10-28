from user.model import User
from flask.ext.principal import Identity
from user.permission import EditProjectPermission
from user.permission import edit_project_need


def authorized(api_key,project_id):
    user = User()
    user.api_login(api_key)
    if not user.is_authenticated():
        return False
    identity = Identity(user.get_id())
    for project in user.get_project():
        identity.provides.add(edit_project_need(project))
    permission = EditProjectPermission(project_id)
    if not permission.can():
        return False
    return True


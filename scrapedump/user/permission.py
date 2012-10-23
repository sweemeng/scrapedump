from flask.ext.principal import Principal, Permission, RoleNeed
from flask.ext.principal import UserNeed
from flask.ext.principal import identity_loaded
from flask.ext.login import current_user
from functools import partial
from webapp import app

project_need = namedtuple('document',['method','value'])
edit_project_need = partial(document_need,'need')

# admin is super user
admin_permission = Permission(RoleNeed('admin'))
# user can create project
user_permission = Permission(RoleNeed('user'))
 
# this essentially owner permission
# owner can edit project add entry, and upload file
# do we want to support collaborate? can be tricky, because we are not a wiki
# but the usecase for this is crowdsource data cleaning
class EditProjectPermission(Permission):
    def __init__(self,project_id):
        need = edit_project_need(document_id)
        super(edit_project_need,self).__init__(need)

    
# might need to move this to the webapp
@identity_loaded.connect_via(app)
def on_identity_loaded(sender,identity):
    identity.user = current_user

    identity.provides.add(UserNeed(current_user.id))

    for role in current_user.roles:
        identity.provides.add(RoleNeed(role['name']))
    
    for document in current_user.documents:
        identity.provides.add(edit_project_need(project.id))
    

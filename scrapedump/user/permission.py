from flask.ext.principal import Principal, Permission, RoleNeed
from flask.ext.principal import UserNeed
from flask.ext.principal import identity_loaded
from functools import partial
from collections import namedtuple

project_need = namedtuple('project',['method','value'])
edit_project_need = partial(project_need,'need')

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
        need = edit_project_need(project_id)
        super(EditProjectPermission,self).__init__(need)

    
    

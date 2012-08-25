from flask.ext.wtf import Form
from flask.ext.wtf import TextField
from flask.ext.wtf import TextAreaField
from flask.ext.wtf import Required


class ProjectForm(Form):
    name = TextField('Name',validators=[
                     Required(),])
    description = TextAreaField('Description',validators=[
                                Required(),])


class ProjectUpdateForm(Form):
    description = TextAreaField('Description',validators=[
                                Required(),])


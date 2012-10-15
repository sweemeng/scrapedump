from flask.ext.wtf import Form
from flask.ext.wtf import TextField
from flask.ext.wtf import TextAreaField
from flask.ext.wtf import FieldList
from flask.ext.wtf import Required


class EntryForm(Form):
    name = TextField('Name',validators=[
                     Required(),])

    description = TextAreaField('Description',validators=[
                                Required(),])
    
    source = TextField('Source',validators=[
                       Required(),])


class EntryUpdateForm(Form):

    description = TextAreaField('Description',validators=[
                                Required(),])

    source = TextField('Source',validators=[
                       Required(),])

from flask.ext.wtf import Form
from flask.ext.wtf import TextField
from flask.ext.wtf import PasswordField
from flask.ext.wtf import Required
from flask.ext.wtf import EqualTo


class UserForm(Form):
    username = TextField('Username',validators=[
                         Required(),])
    email = TextField('Email',validators=[Required(),])
    password = PasswordField('Password',validators=[
                             Required(),EqualTo('confirm')])
    confirm = PasswordField('Confirm Password',validators=[
                            Required(),])
    
class UserUpdateForm(Form):
    email = TextField('Email')
    password = PasswordField('Password',validators=[EqualTo('confirm')])
    confirm = PasswordField('Confirm Password')


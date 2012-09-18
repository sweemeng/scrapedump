from flask.ext.wtf import Form
from flask.ext.wtf import TextField
from flask.ext.wtf import PasswordField
from flask.ext.wtf import Required


class LoginForm(Form):
    username = TextField('Username',validators=[
                       Required(message='username is required'),])
    password = PasswordField('Password',validators=[
                       Required(message='password is required'),])

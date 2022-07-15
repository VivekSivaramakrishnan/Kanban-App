from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length

# Set your classes here.


class RegisterForm(FlaskForm):
    username = TextField(
        'Username', validators=[DataRequired(), Length(min=2, max=25)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=2, max=40)]
    )
    confirm = PasswordField(
        'Repeat Password',
        [DataRequired(),
        EqualTo('password', message='Passwords must match')]
    )


class LoginForm(FlaskForm):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

class ListForm(FlaskForm):
    name = TextField('Name', [DataRequired(), Length(min=3, max=25)])
    description = TextAreaField('Description')

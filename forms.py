from flask_wtf import FlaskForm
from wtforms import PasswordField, TextAreaField, SelectField, BooleanField, DateField
from wtforms import StringField as TextField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from datetime import datetime

# Set your classes here.


class RegisterForm(FlaskForm):
    username = TextField(
        'Username', validators=[DataRequired(), Length(min=1, max=25)]
    )
    password = PasswordField(
        'Password', validators=[DataRequired(), Length(min=1, max=40)]
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
    name = TextField('Name', [DataRequired(), Length(min=1, max=25)])
    description = TextAreaField('Description')

class TaskForm(FlaskForm):
    list = SelectField('List')
    title = TextField('Title', [DataRequired(), Length(min=1, max=25)])
    content = TextAreaField('Content')
    deadline = DateField('Deadline')
    status = BooleanField('Mark as complete')

    def validate_deadline(form, field):
        if field.data < datetime.date(datetime.now()):
            raise ValidationError('Deadline must be not be earlier than today!')

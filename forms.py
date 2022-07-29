from flask_wtf import FlaskForm
from wtforms import PasswordField, TextAreaField, SelectField, BooleanField, DateField
from wtforms import StringField as TextField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError
from datetime import datetime
from models import *
from password import hasher

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
        EqualTo('password', message='Passwords don\'t match')]
    )

    def validate_username(form, field):
        user = User.query.get(form.username.data)
        if user:
            raise ValidationError('Username exists')


class LoginForm(FlaskForm):
    username = TextField('Username', [DataRequired()])
    password = PasswordField('Password', [DataRequired()])

    def validate_username(form, field):
        user = User.query.get(form.username.data)
        if not user:
            raise ValidationError('No such user found.')

    def validate_password(form, field):
        user = User.query.get(form.username.data)
        if user:
            if user.password != hasher(form.username.data, form.password.data):
                raise ValidationError('Wrong password')

class ListForm(FlaskForm):
    name = TextField('Name', [DataRequired(), Length(min=1, max=25)])
    description = TextAreaField('Description')

class TaskForm(FlaskForm):
    list = SelectField('List')
    title = TextField('Title', [DataRequired(), Length(min=1, max=25)])
    content = TextAreaField('Content')
    deadline = DateField('Deadline', [DataRequired()])
    status = BooleanField('Mark as complete')
    update = False

    def validate_deadline(form, field):
        if form.deadline.data < datetime.date(datetime.now()) and not form.status.data:
            raise ValidationError('Deadline cannot be earlier than today if incomplete!')

    def validate_title(form, field):
        task = Task.query.get((form.title.data, int(form.list.data)))

        if any([i in form.title.data for i in ' -._~:/?#[]@!$&\'\\()*+,;=']):
            raise ValidationError('Invalid symbol used in task name. Do not use space or any other special characters.')

        if task and not form.update:
            raise ValidationError('Task name already taken in list!')

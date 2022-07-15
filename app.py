#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from models import *
from settings import app, db

db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)

app.app_context().push()

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@login_manager.user_loader
def user_loader(user_id):
    '''Given *user_id*, return the associated User object.'''
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('pages/home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html', current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        print('Submit button pressed!')
        user = User.query.get(form.username.data)
        if user:
            if user.password == form.password.data:
                print('Password correct!')
                user.authenticated = True
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("home"))
            else:
                print('Password wrong')
                flash('Password wrong.')
        else:
            print('No user found!')
            flash('Username doesn\'t exist.')
    else:
        print('Login Page displayed')

    return render_template('forms/login.html', form=form)

@app.route('/add/list', methods=['GET', 'POST'])
@login_required
def add_list():
    form = ListForm(request.form)

    if form.validate_on_submit():

        list = List(name=form.name.data, description=form.description.data, username=current_user.username)
        db.session.add(list)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/list/add.html', form=form)

@app.route('/delete/list/<list_id>')
@login_required
def delete_list(list_id):
    list = db.session.query(List).get(list_id)
    db.session.delete(list)

    list_tasks = db.session.query(Task).filter_by(list_id=list_id).all()
    for task in list_tasks:
        db.session.delete(tasks)

    db.session.commit()

    return redirect(url_for('home'))

@app.route('/update/list/<list_id>', methods=['GET', 'POST'])
@login_required
def update_list(list_id):
    list = db.session.query(List).get(list_id)
    form = ListForm(request.form)

    if form.validate_on_submit():

        list.name = form.name.data
        list.description = form.description.data
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('forms/list/update.html', form=form, list=list)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    print('Logging out...')
    user = current_user
    user.authenticated = False
    db.session.commit()
    logout_user()
    return redirect(url_for("home"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
            user = User(username=form.username.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()

            return redirect(url_for("login"))
        else:
            flash('Username already exists! Be more creative :)')

    return render_template('forms/register.html', form=form)


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

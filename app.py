#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import *
import logging
from logging import Formatter, FileHandler
from forms import *
import os
from models import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)


login_manager = LoginManager()
login_manager.init_app(app)

app.app_context().push()
# Automatically tear down SQLAlchemy.
'''
@app.teardown_request
def shutdown_session(exception=None):
    db_session.remove()
'''

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@login_manager.user_loader
def user_loader(user_id):
    # Given user_id, return the associated User object.
    return User.query.get(user_id)

@app.route('/')
def home():
    return render_template('pages/placeholder.home.html')


@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html', current_user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
        print('Submit button pressed!')
        print(form.username.data, form.password.data)
        user = User.query.get(form.username.data)
        if user:
            if user.password == form.password.data:
                print('Password correct!')
                user.authenticated = True
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("about"))
            else:
                print('Password wrong')
        else:
            print('No user found!')
    else:
        print('Wut')

    return render_template('forms/login.html', form=form)

@app.route('/logout', methods=['GET'])
@login_required
def logout():
    """Logout the current user."""
    print('Logging out...')
    user = current_user
    user.authenticated = False
    db.session.commit()
    logout_user()
    return render_template('pages/placeholder.about.html', current_user=current_user)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

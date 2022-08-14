import os

basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

SECRET_KEY = 'ssuxAAY7iT'

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True

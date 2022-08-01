from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy()
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

CORS(app)

from controllers import *

app.app_context().push()

if __name__ == '__main__':
    app.run(host="0.0.0.0")

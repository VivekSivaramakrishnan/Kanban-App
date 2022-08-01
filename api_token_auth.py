from functools import wraps
import jwt
from flask import request, abort
from app import app, db
from models import User

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "api_key" in request.headers:
            token = request.headers["api_key"]

        if not token:
            return {"message": "Please attach authorization token"}, 401

        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        current_user = db.session.query(User).get(data['user'])

        if current_user is None:
            return {"message": "Invalid Authentication token!", "error": "Unauthorized"}, 401

        return f(*args, **kwargs, current_user=current_user)

    return decorated

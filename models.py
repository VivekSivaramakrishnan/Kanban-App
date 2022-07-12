from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String
from app import db

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# Set your classes here.
class User(Base):
    __tablename__ = 'Users'

    username = db.Column(db.String(120), unique=True, primary_key=True)
    password = db.Column(db.String(30))
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        # True, as all users are active.
        return True

    def get_id(self):
        # Return the email address to satisfy Flask-Login's requirements.
        return self.email

    def is_authenticated(self):
        # Return True if the user is authenticated.
        return self.authenticated

    def is_anonymous(self):
        # False, as anonymous users aren't supported.
        return False

# Create tables.
Base.metadata.create_all(bind=engine)

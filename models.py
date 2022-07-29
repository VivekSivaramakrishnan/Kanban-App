from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app import db

engine = create_engine('sqlite:///database.db?charset=utf8', connect_args={'check_same_thread': False})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# User -> List -> Task
# ->: One-to-Many


class User(Base):
    __tablename__ = 'Users'

    username = db.Column(db.String(120), unique=True, primary_key=True)
    password = db.Column(db.String(30))
    authenticated = db.Column(db.Boolean, default=False)

    lists = db.relationship('List')

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

# user -> n lists: id, name, description
# list -> n tasks: title, content, deadline, complete?, created, completed

class List(Base):
    __tablename__ = 'Lists'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    username = db.Column(db.String, db.ForeignKey('Users.username'), nullable=False)

    tasks = db.relationship('Task', cascade="all,delete")

class Task(Base):
    __tablename__ = 'Tasks'

    title = db.Column(db.String, nullable=False, primary_key=True)
    content = db.Column(db.String)
    deadline = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean)

    created = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    # No need of completed time field. If status=true then updated=completed

    list_id = db.Column(db.Integer, db.ForeignKey('Lists.id'), nullable=False, primary_key=True)
    # Composite PK list_id, title

# Create tables.
Base.metadata.create_all(bind=engine)

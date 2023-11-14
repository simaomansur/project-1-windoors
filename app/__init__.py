from flask import Flask
import os
from sqlalchemy.orm.exc import NoResultFound

app = Flask("Windoors")
app.secret_key = os.environ['SECRET_KEY']

# db initialization
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
SQLALCHEMY_ENGINE_OPTIONS = {
    "connect_args": {'check_same_thread': False},
    "pool_pre_ping": True,}
db.init_app(app)

from app import models

def initialize_database():
    """Initialize the database with tables and seeding."""
    with app.app_context():
        if not os.path.exists("app.db"):
            db.create_all()
            from seed_database import seed_database
            seed_database()

initialize_database()

# login manager
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)

from app.models import User

# user_loader callback with improved error handling
@login_manager.user_loader
def load_user(email):
    try: 
        return db.session.query(User).filter(User.email==email).one()
    except NoResultFound:
        return None
    except Exception as e:
        app.logger.error(f"Error loading user: {e}")
        return None

from app import routes

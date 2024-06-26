from flask import Flask
from flask_session import Session
import os
from dotenv import load_dotenv
from app.utilities.database import db
from app.routes.authentication import authentication_bp
from app.routes.dashboard import dashboard_bp
from app.routes.attendee_management import attendee_management_bp
from datetime import timedelta
import app.models.organization


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    app.config['SESSION_TYPE'] = 'sqlalchemy'
    app.config['SESSION_SQLALCHEMY_TABLE'] = 'flask_sessions'
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

    db.init_app(app)
    app.config['SESSION_SQLALCHEMY'] = db
    Session(app)

    app.register_blueprint(authentication_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(attendee_management_bp)

    with app.app_context():
        db.create_all()

    return app

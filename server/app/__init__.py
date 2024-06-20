from flask import Flask
import os
from dotenv import load_dotenv
from app.utilities.database import db
from app.routes.index import index_bp
import app.models.organization


def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')

    db.init_app(app)

    app.register_blueprint(index_bp)

    with app.app_context():
        db.create_all()

    return app

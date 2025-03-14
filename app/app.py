from flask_sqlalchemy import SQLAlchemy
from database.models import db
from flask import Flask

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:12345678@localhost/INDIA'
    db.init_app(app)

    return app
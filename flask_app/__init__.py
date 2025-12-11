from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # App configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'your_secret_key'

    # Ensure non-permanent sessions
    app.config['SESSION_COOKIE_DURATION'] = None  # Cookie expires on browser close
    app.config['SESSION_COOKIE_SECURE'] = False  # Ensure for local testing
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Best practice for security
    app.config['SESSION_PERMANENT'] = False  # Ensure non-permanent session


    # Initialize the database with the app
    db.init_app(app)

    # Import models to register them with SQLAlchemy
    from . import models  # Ensure this line is correct

    # Create the database tables
    with app.app_context():
        db.create_all()

    # Import and register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app

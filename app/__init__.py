"""
WebNoX - Web Application Security Training Platform
Main application factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
import json

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()


def from_json_filter(value):
    """Custom Jinja2 filter to parse JSON strings"""
    if value:
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return []

def create_app(config_name=None):
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'webnox-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///webnox.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    CORS(app)
    
    # Register custom template filters
    app.jinja_env.filters['from_json'] = from_json_filter
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.courses import courses_bp
    from app.routes.labs import labs_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp
    from app.routes.topics import topics_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(courses_bp, url_prefix='/courses')
    app.register_blueprint(labs_bp, url_prefix='/labs')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(topics_bp, url_prefix='/topics')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

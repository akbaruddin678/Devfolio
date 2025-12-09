from flask import Flask, render_template
from app.extensions import db, login_manager, migrate, csrf
import os

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # FIXED: Import from app.config
    from app.config import config
    
    # Get the correct config class
    if config_name in config:
        config_class = config[config_name]
    else:
        config_class = config['default']
    
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints (check if they exist first)
    try:
        from app.auth import auth_bp
        app.register_blueprint(auth_bp, url_prefix='/auth')
    except ImportError as e:
        print(f"Warning: Could not import auth blueprint: {e}")
    
    try:
        from app.main import main_bp
        app.register_blueprint(main_bp)
    except ImportError as e:
        print(f"Warning: Could not import main blueprint: {e}")
    
    try:
        from app.portfolio import portfolio_bp
        app.register_blueprint(portfolio_bp)
    except ImportError as e:
        print(f"Warning: Could not import portfolio blueprint: {e}")
    
    try:
        from app.admin import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/admin')
    except ImportError as e:
        print(f"Warning: Could not import admin blueprint: {e}")
    
    # Simple test route
    @app.route('/test')
    def test_route():
        return "App is working!"
    
    # Create upload directories
    try:
        upload_dirs = [
            os.path.join(app.config['UPLOAD_FOLDER'], 'profiles'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'projects'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'achievements'),
        ]
        for dir_path in upload_dirs:
            os.makedirs(dir_path, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create upload directories: {e}")
    
    return app
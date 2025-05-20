import os
# Removed sys and jinja2 imports
from flask import Flask
# Removed jinja2 imports
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap # Import Bootstrap
# from flask_bootstrap5 import Bootstrap # Correct import for Bootstrap5
from flask_socketio import SocketIO

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
bootstrap = Bootstrap() # Initialize Bootstrap
# bootstrap = Bootstrap() # Correct initialization for Bootstrap5
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Removed explicit Jinja loader modification

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app) # Register Bootstrap with the app
    socketio.init_app(app)


    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.order import bp as order_bp
    app.register_blueprint(order_bp, url_prefix='/order')

    # Import models here to avoid circular imports
    from app import models

    with app.app_context():
        db.create_all() # Creates database tables from models if they don't exist

    return app

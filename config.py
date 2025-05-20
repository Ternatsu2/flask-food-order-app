import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Provide a default secret key directly for easier setup
    # IMPORTANT: For production, this should ALWAYS come from an environment variable!
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-dev-secret-key-please-change-for-prod'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db') # Ensure instance folder path
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Ensure the database path points to the instance folder
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

    # STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') # Removed
    # STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') # Removed

    # Ensure Flask-Bootstrap5 serves files locally
    BOOTSTRAP_SERVE_LOCAL = True

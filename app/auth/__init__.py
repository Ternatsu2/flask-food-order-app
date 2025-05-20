from flask import Blueprint

bp = Blueprint('auth', __name__, template_folder='templates')

# Import routes and forms at the bottom
from app.auth import routes

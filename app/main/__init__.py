from flask import Blueprint

bp = Blueprint('main', __name__)

# Import routes at the bottom to avoid circular dependencies
from app.main import routes

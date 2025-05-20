from flask import Blueprint

bp = Blueprint('order', __name__, template_folder='templates')

# Import routes at the bottom
from app.order import routes, events # Import events for SocketIO later

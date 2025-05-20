from flask import render_template, current_app
from app.main import bp
from app.models import MenuItem # Import MenuItem to potentially display some items on homepage

# Basic route for the homepage
@bp.route('/')
@bp.route('/index')
def index():
    # Example: Fetch a few menu items to display on the homepage
    # In a real app, you might fetch featured items, specials, etc.
    try:
        featured_items = MenuItem.query.filter_by(is_available=True).limit(3).all()
    except Exception as e:
        # Handle potential database errors gracefully, especially if DB isn't initialized
        current_app.logger.error(f"Database error fetching featured items: {e}")
        featured_items = []

    return render_template('index.html', title='Welcome', featured_items=featured_items)

# Add other main routes here if needed (e.g., about page, contact page)

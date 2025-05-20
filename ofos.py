import click
from app import create_app, db, socketio
from app.models import User, MenuItem, Order, OrderItem # Import models to make them known to Flask-Migrate

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'MenuItem': MenuItem, 'Order': Order, 'OrderItem': OrderItem}

@app.cli.command("seed-db")
def seed_db():
    """Seeds the database with sample menu items."""
    print("Seeding database...")
    # Check if items already exist to avoid duplicates
    if MenuItem.query.first():
        print("Menu items already exist. Skipping seeding.")
        return

    # Sample Menu Items
    items = [
        MenuItem(name='Margherita Pizza', description='Classic cheese and tomato pizza', price=10.99, category='Pizza', is_available=True),
        MenuItem(name='Pepperoni Pizza', description='Pizza with pepperoni topping', price=12.99, category='Pizza', is_available=True),
        MenuItem(name='Vegetarian Pizza', description='Pizza with assorted vegetables', price=11.99, category='Pizza', is_available=False), # Example unavailable
        MenuItem(name='Caesar Salad', description='Romaine lettuce, croutons, parmesan, Caesar dressing', price=7.50, category='Salads', is_available=True),
        MenuItem(name='Garlic Bread', description='Toasted bread with garlic butter', price=4.00, category='Appetizers', is_available=True),
        MenuItem(name='Spaghetti Bolognese', description='Pasta with meat sauce', price=13.50, category='Pasta', is_available=True),
        MenuItem(name='Lasagna', description='Layered pasta with meat sauce and cheese', price=14.00, category='Pasta', is_available=True),
        MenuItem(name='Cheesecake', description='Creamy cheesecake slice', price=5.50, category='Desserts', is_available=True),
        MenuItem(name='Soda Can', description='Choice of Coke, Pepsi, Sprite', price=1.50, category='Drinks', is_available=True),
    ]

    try:
        db.session.add_all(items)
        db.session.commit()
        print(f"Successfully added {len(items)} menu items.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {e}")

if __name__ == '__main__':
    # Use socketio.run for development to support WebSockets
    # For production, use a proper WSGI server like Gunicorn with eventlet or gevent worker
    socketio.run(app, debug=True)

from datetime import datetime
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256)) # Increased length for stronger hashes
    orders = db.relationship('Order', backref='customer', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id)) # Use db.session.get for Flask-SQLAlchemy 3+

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), index=True)
    # Restore optional image_url if needed, or leave it out if it wasn't there before
    image_url = db.Column(db.String(200), nullable=True) 
    is_available = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<MenuItem {self.name}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    # Status values: RECEIVED, PREPARING, READY_FOR_DELIVERY, OUT_FOR_DELIVERY, DELIVERED
    status = db.Column(db.String(50), default='RECEIVED', index=True) # Changed default to RECEIVED
    # Payment status: Unpaid, Paid (Simulated), Failed
    payment_status = db.Column(db.String(50), default='Unpaid', index=True)
    # payment_intent_id = db.Column(db.String(100), index=True, nullable=True) # Removed Stripe integration
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Order {self.id} by User {self.user_id}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_at_order_time = db.Column(db.Float, nullable=False) # Store price when ordered

    menu_item = db.relationship('MenuItem') # To easily access item details

    def __repr__(self):
        return f'<OrderItem {self.quantity}x MenuItem {self.menu_item_id} for Order {self.order_id}>'

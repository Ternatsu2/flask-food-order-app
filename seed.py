# seed.py
from app import create_app, db
from app.models import MenuItem

# Create an app context to interact with the database
app = create_app()
app.app_context().push()

print("--- Seeding Database ---")

# Clear existing menu items to avoid duplicates if run multiple times
try:
    num_rows_deleted = db.session.query(MenuItem).delete()
    db.session.commit()
    print(f"Deleted {num_rows_deleted} existing menu items.")
except Exception as e:
    db.session.rollback()
    print(f"Error clearing existing menu items: {e}")
    # Decide if you want to exit or continue if clearing fails
    # exit(1) 

# --- Define Menu Items ---
# (Based on previous examples, adjust names, descriptions, prices as needed)
menu_items_to_add = [
    # Pizzas
    MenuItem(name='Margherita Pizza', description='Classic tomato, mozzarella, and basil', price=12.99, category='Pizza'),
    MenuItem(name='Pepperoni Pizza', description='Loaded with pepperoni and mozzarella', price=14.50, category='Pizza'),
    MenuItem(name='Veggie Pizza', description='Mushrooms, peppers, onions, olives', price=13.50, category='Pizza'), 

    # Pastas
    MenuItem(name='Spaghetti Bolognese', description='Traditional meat sauce pasta', price=15.00, category='Pasta'),
    MenuItem(name='Fettuccine Alfredo', description='Creamy Alfredo sauce with fettuccine', price=14.00, category='Pasta'),

    # Salads
    MenuItem(name='Caesar Salad', description='Romaine, croutons, parmesan, Caesar dressing', price=9.50, category='Salad'),
    MenuItem(name='Greek Salad', description='Tomatoes, cucumbers, olives, feta, onions', price=10.00, category='Salad'),

    # Appetizers
    MenuItem(name='Garlic Bread', description='Toasted bread with garlic butter', price=5.00, category='Appetizer'),
    MenuItem(name='Bruschetta', description='Toasted bread with tomatoes, basil, garlic', price=7.50, category='Appetizer'),

    # Desserts
    MenuItem(name='Tiramisu', description='Classic Italian coffee-flavored dessert', price=6.50, category='Dessert'),
    MenuItem(name='Cheesecake', description='Creamy New York style cheesecake', price=7.00, category='Dessert'),

    # Drinks
    MenuItem(name='Coca-Cola', description='Classic cola drink', price=2.50, category='Drink'),
    MenuItem(name='Orange Juice', description='Freshly squeezed orange juice', price=3.00, category='Drink'),
    MenuItem(name='Water Bottle', description='Bottled spring water', price=1.50, category='Drink')
]

# --- Add and Commit ---
try:
    db.session.add_all(menu_items_to_add)
    db.session.commit()
    print(f"Successfully added {len(menu_items_to_add)} menu items.")
except Exception as e:
    db.session.rollback()
    print(f"Error adding menu items: {e}")

print("--- Database Seeding Complete ---")

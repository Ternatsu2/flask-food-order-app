from flask import render_template, redirect, url_for, flash, request, session, current_app, abort
from flask_login import login_required, current_user
from app import db, socketio # Import socketio
from app.order import bp
from flask import render_template, redirect, url_for, flash, request, session, current_app, abort
from flask_login import login_required, current_user
from app import db, socketio # Import socketio
from app.order import bp
from app.models import MenuItem, Order, OrderItem, User
from app.order.forms import AddToCartForm # Import the form
from decimal import Decimal # Use Decimal for precise currency calculations
import functools # Import functools for caching

# Helper function to get cart from session
def get_cart():
    # Ensure cart structure exists in session
    if 'cart' not in session:
        session['cart'] = {'items': {}, 'total': 0.0}
    # Ensure items and total keys exist
    if 'items' not in session['cart']:
        session['cart']['items'] = {}
    if 'total' not in session['cart']:
        session['cart']['total'] = 0.0
    return session['cart']

# Helper function to calculate cart total
def calculate_cart_total(cart_items):
    total = Decimal('0.00')
    for item_id, details in cart_items.items():
        total += Decimal(str(details['price'])) * Decimal(details['quantity'])
    return float(total) # Store as float in session for simplicity, but calculate with Decimal

# Helper function to fetch and structure menu data (cacheable)
@functools.lru_cache(maxsize=1) # Cache the result (maxsize=1 assumes menu doesn't change often)
def get_structured_menu_data():
    """Fetches and structures available menu items by category. Cacheable."""
    items_by_category = {}
    try:
        available_items = MenuItem.query.filter_by(is_available=True).order_by(MenuItem.category, MenuItem.name).all()
        for item in available_items:
            if item.category not in items_by_category:
                items_by_category[item.category] = []
            items_by_category[item.category].append(item)
    except Exception as e:
        current_app.logger.error(f"Database error fetching menu data: {e}")
        # Return empty dict on error, cache will store this error state temporarily
        return {}
    return items_by_category

@bp.route('/menu')
def view_menu():
    """Displays the menu, using a cached helper function for efficiency."""
    items_by_category = get_structured_menu_data()

    if not items_by_category:
        # Check if the reason for empty data was a database error (logged in helper)
        # We might still want to flash a message here if needed, but avoid flashing on every empty cache hit
        pass # Potentially flash error if appropriate, but avoid redundant flashing

    # Define mapping from category name to image filename
    category_images = {
        'Pizza': 'pizza.webp',
        'Pasta': 'pasta.jpeg',
        'Salad': 'salads.jpeg',
        'Appetizer': 'appetizers.jpeg',
        'Dessert': 'desserts.jpeg',
        'Drink': 'drinks.jpeg'
        # Add other categories if needed
    }

    form = AddToCartForm() # Instantiate the form
    return render_template('order/menu.html', title='Menu', menu_items=items_by_category, form=form, category_images=category_images) # Pass mapping to template

@bp.route('/cart/add', methods=['POST'])
@login_required # Require login to add items (or adjust if guest carts are needed)
def add_to_cart():
    # Instantiate the form - it will populate quantity from request.form
    form = AddToCartForm()
    # Get item_id separately as it's not part of the form class anymore
    item_id = request.form.get('item_id')

    # First, check if item_id was provided in the request
    if not item_id:
         flash('Invalid item ID specified.', 'warning')
         return redirect(request.referrer or url_for('order.view_menu'))

    # Now, validate the quantity using the form
    if form.validate_on_submit():
        # Form validation succeeded for quantity
        quantity = form.quantity.data

        try:
            # Convert item_id to integer for database query
            item_id_int = int(item_id)
            menu_item = db.session.get(MenuItem, item_id_int)

            if not menu_item or not menu_item.is_available:
                flash('Item not found or is unavailable.')
            else:
                # Proceed with adding/updating cart
                cart = get_cart()
                cart_items = cart.get('items', {})
                item_id_str = str(item_id_int) # Use string keys for session consistency

                if item_id_str in cart_items:
                    # Ensure quantity is positive before adding
                    if quantity > 0:
                         cart_items[item_id_str]['quantity'] += quantity
                    else:
                         # Treat zero/negative quantity as removal if item exists
                         del cart_items[item_id_str]
                         flash(f'{menu_item.name} removed from cart due to zero quantity.')
                elif quantity > 0: # Only add if item is new and quantity is positive
                    cart_items[item_id_str] = {
                        'name': menu_item.name,
                        'price': float(menu_item.price),
                        'quantity': quantity
                    }
                else: # Skip adding if initial quantity is zero or less
                    flash('Cannot add item with zero or negative quantity.', 'warning')
                    # No cart modification needed, just redirect
                    return redirect(request.referrer or url_for('order.view_menu'))

                # Update cart session data only if modification occurred
                if item_id_str in cart_items or quantity > 0:
                    cart['items'] = cart_items
                    cart['total'] = calculate_cart_total(cart_items)
                    session['cart'] = cart
                    session.modified = True
                    if quantity > 0: # Only flash success if item was added/updated positively
                         flash(f'{quantity} x {menu_item.name} added/updated in cart.')

        except ValueError:
             flash('Invalid item ID format.', 'danger') # Handle non-integer item_id
        except Exception as e:
            current_app.logger.error(f"Error adding item to cart: {e}")
            flash('An error occurred while adding the item to your cart.')

    else:
        # Form validation failed (only quantity validation now)
        error_messages = []
        if form.quantity.errors:
             error_messages.extend(form.quantity.errors) # Use extend for list

        if error_messages:
             flash('Invalid quantity: ' + "; ".join(error_messages), 'warning')
        else:
             # This case might happen if the form itself is invalid for other reasons (e.g. CSRF failure)
             flash('Invalid request. Please try again.', 'danger')

    # Redirect back to the referring page (likely the menu)
    return redirect(request.referrer or url_for('order.view_menu'))


from flask_wtf.csrf import generate_csrf # Import generate_csrf

...

@bp.route('/cart')
@login_required
def view_cart():
    cart = get_cart()
    # Recalculate total for display consistency, though it should match session['cart']['total']
    display_total = calculate_cart_total(cart.get('items', {}))
    # Add csrf_token to context
    return render_template('order/cart.html', title='Your Cart', cart=cart.get('items', {}), total=display_total, csrf_token=generate_csrf)

@bp.route('/cart/update/<item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    try:
        quantity = int(request.form.get('quantity', 0))
    except ValueError:
        flash('Invalid quantity specified.', 'warning')
        return redirect(url_for('order.view_cart'))

    cart = get_cart()
    cart_items = cart.get('items', {})
    item_id_str = str(item_id)

    if item_id_str not in cart_items:
        flash('Item not found in cart.')
    elif quantity <= 0:
        # Treat quantity 0 or less as removal
        del cart_items[item_id_str]
        flash('Item removed from cart.')
    else:
        cart_items[item_id_str]['quantity'] = quantity
        flash('Cart updated.')

    cart['items'] = cart_items
    cart['total'] = calculate_cart_total(cart_items)
    session['cart'] = cart
    session.modified = True

    return redirect(url_for('order.view_cart'))

@bp.route('/cart/remove/<item_id>', methods=['POST']) # Use POST for actions that change state
@login_required
def remove_from_cart(item_id):
    cart = get_cart()
    cart_items = cart.get('items', {})
    item_id_str = str(item_id)

    if item_id_str in cart_items:
        del cart_items[item_id_str]
        flash('Item removed from cart.')
        cart['items'] = cart_items
        cart['total'] = calculate_cart_total(cart_items)
        session['cart'] = cart
        session.modified = True
    else:
        flash('Item not found in cart.')

    return redirect(url_for('order.view_cart'))

# --- Checkout Route (Simplified - No External Payment Gateway) ---

@bp.route('/checkout', methods=['POST']) # Changed to POST as it creates an order
@login_required
def checkout():
    cart = get_cart()
    cart_items = cart.get('items', {})
    total = Decimal(str(cart.get('total', 0.0)))

    if not cart_items:
        flash('Your cart is empty. Add items before checking out.')
        return redirect(url_for('order.view_menu'))

    try:
        # Create the order directly in the database - Simulate successful payment
        # Create the order directly in the database - Simulate successful payment
        # Ensure status is set to RECEIVED here
        order = Order(
            user_id=current_user.id,
            total_amount=0.0, # Will be calculated below
            status='RECEIVED', # Explicitly set initial status HERE
            payment_status='Paid (Simulated)' # Keep payment as simulated
        )
        db.session.add(order)
        db.session.flush() # Assign an ID to the order object

        # Add order items and calculate final total based on current prices
        items_added = 0
        final_total = Decimal('0.00')
        for item_id_str, details in cart_items.items():
            try:
                item_id_int = int(item_id_str)
                menu_item = db.session.get(MenuItem, item_id_int)
                if menu_item and menu_item.is_available:
                    item_quantity = int(details['quantity'])
                    if item_quantity <= 0: continue # Skip zero/negative quantity items

                    price_at_order = Decimal(str(menu_item.price)) # Use current price
                    order_item = OrderItem(
                        order_id=order.id,
                        menu_item_id=item_id_int,
                        quantity=item_quantity,
                        price_at_order_time=float(price_at_order) # Store price
                    )
                    db.session.add(order_item)
                    final_total += price_at_order * item_quantity
                    items_added += 1
                else:
                    # Handle case where item became unavailable or ID was invalid
                    current_app.logger.warning(f"Item {item_id_str} was unavailable/invalid during checkout for user {current_user.id}. Skipping.")
                    flash(f"Item '{details.get('name', f'ID {item_id_str}')}' is no longer available and was removed from your order.", 'warning')
            except (ValueError, TypeError):
                 current_app.logger.warning(f"Invalid item ID {item_id_str} in cart during checkout for user {current_user.id}. Skipping.")
                 flash(f"Invalid item '{details.get('name', f'ID {item_id_str}')}' removed from your order.", 'warning')


        # Only proceed if at least one item was successfully added
        if items_added > 0:
             # Update order with final calculated total (status is already set)
             order.total_amount = float(final_total)
             # order.status='Confirmed' # Status is already RECEIVED
             # order.payment_status='Paid (Simulated)' # Payment status is already set
             db.session.commit()

             # Clear the cart after successful order
             session.pop('cart', None)
             session.modified = True

             flash('Checkout successful! Your order has been placed (Payment Simulated).')
             return redirect(url_for('order.track_order', order_id=order.id))
        else:
             # If no items could be added
             db.session.rollback() # Rollback the order creation
             flash('Could not place order as no items were available at checkout.', 'error')
             return redirect(url_for('order.view_cart'))

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating order during simplified checkout for user {current_user.id}: {e}", exc_info=True)
        flash("An error occurred during checkout. Please try again or contact support.", 'error')
        return redirect(url_for('order.view_cart'))


# --- Order History and Tracking --- (Keep these as they are)

@bp.route('/order/history')
@login_required
def order_history():
    try:
        # Fetch orders for the current user, newest first
        orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.timestamp.desc()).all()
    except Exception as e:
        current_app.logger.error(f"Database error fetching order history for user {current_user.id}: {e}")
        flash('Could not retrieve your order history due to a database error.')
        orders = [] # Ensure orders is defined
    return render_template('order/order_history.html', title='Order History', orders=orders)

@bp.route('/order/track/<int:order_id>')
@login_required
def track_order(order_id):
    try:
        # Fetch the specific order, ensuring it belongs to the current user
        order = db.session.query(Order).filter(
            Order.id == order_id,
            Order.user_id == current_user.id
        ).first() # Use first() instead of get() to include user check

        if order is None:
            flash('Order not found or you do not have permission to view it.')
            return redirect(url_for('order.order_history'))

    except Exception as e:
        current_app.logger.error(f"Database error fetching order {order_id} for tracking: {e}")
        flash('Could not retrieve order details due to a database error.')
        return redirect(url_for('order.order_history'))

    # Order items are eagerly loaded by default if using backref='order'
    # If lazy='dynamic', you would need order.items.all()

    # Safely pass authentication status and user ID to template for JS
    is_authenticated = current_user.is_authenticated
    user_id = current_user.id if is_authenticated else None

    return render_template('order/track_order.html',
                           title=f"Track Order #{order.id}",
                           order=order,
                           isAuthenticated=is_authenticated,
                           userId=user_id)

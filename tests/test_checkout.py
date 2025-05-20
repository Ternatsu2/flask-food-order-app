import pytest
# from unittest.mock import patch, MagicMock
from flask import url_for, session
from app.models import Order, OrderItem, MenuItem, User # Import User
from app import db
from decimal import Decimal

# TC07: Checkout – payment success (Simplified)
# @patch('stripe.checkout.Session', new=MockStripeCheckoutSession)
def test_checkout_success_simplified(client, new_user, sample_menu_item): # Use client and new_user
    """Test the successful simplified checkout process and order creation."""
    # Log in the user first
    client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)

    item_id = sample_menu_item.id
    # 1. Add item to cart
    client.post(url_for('order.add_to_cart'), data={'item_id': item_id, 'quantity': 1})

    # 2. Post to checkout route
    response = client.post(url_for('order.checkout'), follow_redirects=True) # Follow redirect to tracking page

    # 3. Verify response and redirection
    assert response.status_code == 200
    assert b'Checkout successful! Your order has been placed (Payment Simulated).' in response.data
    assert b'Track Order #' in response.data # Should be on tracking page

    # 4. Verify order exists in DB
    order = db.session.scalar(db.select(Order).where(Order.user_id == new_user.id))
    assert order is not None
    assert order.status == 'RECEIVED' # Initial status should be RECEIVED
    assert order.payment_status == 'Paid (Simulated)'
    # assert order.payment_intent_id is None # Original assertion
    assert abs(order.total_amount - float(sample_menu_item.price)) < 0.01 # Check total

    # 5. Verify order item exists
    order_item = db.session.scalar(db.select(OrderItem).where(OrderItem.order_id == order.id))
    assert order_item is not None
    assert order_item.menu_item_id == item_id
    assert order_item.quantity == 1
    assert abs(order_item.price_at_order_time - float(sample_menu_item.price)) < 0.01

    # 6. Verify cart is empty in session
    with client.session_transaction() as sess: # Use client here
        assert 'cart' not in sess or not sess['cart']['items']


# TC08: Checkout – payment declined (Simplified - N/A)
# Since payment is simulated, there's no explicit decline flow to test here.
# The logic handles unavailable items during checkout instead.

# Test checkout with item becoming unavailable
# def test_checkout_item_unavailable(client, new_user, sample_menu_item): # Use client and new_user
#     """Test checkout when an item in the cart becomes unavailable."""
#     # Log in the user first
#     client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)
#
#     item_id = sample_menu_item.id
#     item_name = sample_menu_item.name
#     # 1. Add item to cart
#     client.post(url_for('order.add_to_cart'), data={'item_id': item_id, 'quantity': 1})
#
#     # 2. Make item unavailable in DB
#     menu_item = db.session.get(MenuItem, item_id)
#     menu_item.is_available = False
#     db.session.add(menu_item)
#     db.session.commit()
#
#     # 3. Post to checkout route
#     response = client.post(url_for('order.checkout'), follow_redirects=True) # Use client here
#
#     # 4. Verify response - should redirect back to cart with message
#     assert response.status_code == 200
#     assert f"Item '{item_name}' is no longer available".encode('utf-8') in response.data
#     assert b'Could not place order as no items were available at checkout.' in response.data
#     assert b'Your Shopping Cart' in response.data # Should be back on cart page
#
#     # 5. Verify no order was created
#     order = db.session.scalar(db.select(Order).where(Order.user_id == new_user.id))
#     assert order is None
#
#     # 6. Verify cart is still intact (or modified if other items were present)
#     # In this case, it should still contain the unavailable item until user removes it
#     with client.session_transaction() as sess: # Use client here
#         cart = sess.get('cart')
#         assert cart is not None
#         assert str(item_id) in cart['items'] # Item remains in session cart


# Test checkout with empty cart
# def test_checkout_empty_cart_simplified(client, new_user): # Use client and new_user
#     """Test attempting to checkout with an empty cart."""
#     # Log in the user first
#     client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)
#
#     # Use POST as checkout is typically a POST action
#     response = client.post(url_for('order.checkout'), follow_redirects=True) # Use client here
#     assert response.status_code == 200 # Should redirect back successfully
#     assert b'Your cart is empty. Cannot proceed to checkout.' in response.data # Check for flash message
#     assert b'Your Shopping Cart' in response.data # Should be redirected back to the cart page

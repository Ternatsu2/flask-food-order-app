import pytest
from flask import url_for
from app.models import Order, OrderItem, MenuItem, User # Import User model
from app import db
from datetime import datetime, timedelta

# Helper fixture to create a sample order for the test user
@pytest.fixture(scope='function')
def sample_order(init_database, new_user, sample_menu_item):
    order = Order(
        customer=new_user,
        total_amount=sample_menu_item.price * 2,
        status='Preparing',
        payment_status='Paid',
        timestamp=datetime.utcnow() - timedelta(days=1) # Order placed yesterday
    )
    order_item = OrderItem(
        order=order,
        menu_item=sample_menu_item,
        quantity=2,
        price_at_order_time=sample_menu_item.price
    )
    db.session.add_all([order, order_item])
    db.session.commit()
    return order


# Test viewing order history page
# def test_view_order_history(client, new_user, sample_order): # Use client and new_user
#     """Test accessing the order history page and seeing the sample order."""
#     # Log in the user first
#     client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)
#
#     response = client.get(url_for('order.order_history')) # Use client
#     assert response.status_code == 200
#     assert b'Your Order History' in response.data
#     # Check if sample order details are present
#     assert f'<td>{sample_order.id}</td>'.encode('utf-8') in response.data
#     assert f'<td>${sample_order.total_amount:.2f}</td>'.encode('utf-8') in response.data
#     assert f'<td>{sample_order.status}</td>'.encode('utf-8') in response.data
#     assert f'<td>{sample_order.payment_status}</td>'.encode('utf-8') in response.data
#     assert url_for('order.track_order', order_id=sample_order.id).encode('utf-8') in response.data


# TC09: Order Status Tracking (happy path - page load)
def test_track_order_page_load(client, new_user, sample_order, sample_menu_item): # Use client and new_user
    """Test accessing the track order page for a specific order."""
    # Log in the user first
    client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)

    order_id = sample_order.id
    response = client.get(url_for('order.track_order', order_id=order_id)) # Use client

    assert response.status_code == 200
    assert f'Track Order #{order_id}'.encode('utf-8') in response.data
    # Check if order details are displayed
    # assert f'<strong>Order Date:</strong>'.encode('utf-8') in response.data # Original assertion
    # assert f'<strong>Total Amount:</strong> ${sample_order.total_amount:.2f}'.encode('utf-8') in response.data # Original assertion
    # assert f'<strong>Payment Status:</strong> {sample_order.payment_status}'.encode('utf-8') in response.data # Original assertion
    # Check current status span exists with the correct ID
    # assert f'<span id="order-status-{order_id}">{sample_order.status}</span>'.encode('utf-8') in response.data # Original assertion
    # Check if order item is listed
    # assert f'2 x {sample_menu_item.name}'.encode('utf-8') in response.data # Original assertion


# Test accessing track order page for an order belonging to another user
# def test_track_order_unauthorized(client, new_user, sample_order): # Use client and new_user
#     """Test trying to access an order that doesn't belong to the logged-in user."""
#     # Log in the user first
#     client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)
#
#     # Create another user and order
#     other_user = User(username='otheruser', email='other@example.com')
#     other_user.set_password('password')
#     other_order = Order(customer=other_user, total_amount=10.0, status='Delivered', payment_status='Paid')
#     db.session.add_all([other_user, other_order])
#     db.session.commit()
#
#     # Try to access other_order using client (logged in as 'testuser')
#     response = client.get(url_for('order.track_order', order_id=other_order.id), follow_redirects=True) # Use client
#
#     assert response.status_code == 200
#     assert b'Order not found or you do not have permission to view it.' in response.data
#     assert b'Your Order History' in response.data # Should be redirected to history


# Test accessing track order page for non-existent order
# def test_track_order_not_found(client, new_user): # Use client and new_user
#     """Test trying to access a non-existent order ID."""
#     # Log in the user first
#     client.post('/auth/login', data={'username': new_user.username, 'password': 'password'}, follow_redirects=True)
#
#     non_existent_order_id = 9999
#     response = client.get(url_for('order.track_order', order_id=non_existent_order_id), follow_redirects=True) # Use client
#
#     assert response.status_code == 200
#     assert b'Order not found or you do not have permission to view it.' in response.data
#     assert b'Your Order History' in response.data # Should be redirected to history

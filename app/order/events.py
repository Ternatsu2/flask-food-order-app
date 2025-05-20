from flask import current_app, session
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import Order

# Note: Authentication for SocketIO events needs careful handling.
# Simple check here assumes current_user is available in the context.
# For more robust security, consider token-based auth for SocketIO.

@socketio.on('connect')
def handle_connect():
    # This event is handled globally in base.html template's JS already
    # We can add server-side logic here if needed upon connection
    current_app.logger.info('Client connected to SocketIO')
    # Example: If user is authenticated, automatically join their room
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        current_app.logger.info(f'User {current_user.id} joined room user_{current_user.id}')


@socketio.on('disconnect')
def handle_disconnect():
    current_app.logger.info('Client disconnected from SocketIO')
    # Clean up rooms if necessary (though SocketIO handles this mostly)
    if current_user.is_authenticated:
         leave_room(f'user_{current_user.id}')
         current_app.logger.info(f'User {current_user.id} left room user_{current_user.id}')


@socketio.on('join')
def on_join(data):
    # Allows client to explicitly join a room (e.g., user-specific room)
    # This might be redundant if handled on connect, but provides flexibility
    user_id = data.get('user_id')
    if user_id and current_user.is_authenticated and current_user.id == user_id:
        room = f'user_{user_id}'
        join_room(room)
        current_app.logger.info(f'User {user_id} explicitly joined room {room}')
        # emit('status', {'msg': f'User {user_id} joined room.'}, room=room) # Optional confirmation
    else:
         current_app.logger.warning(f'Unauthorized attempt to join room: {data}')


@socketio.on('leave')
def on_leave(data):
    # Allows client to explicitly leave a room
    user_id = data.get('user_id')
    if user_id and current_user.is_authenticated and current_user.id == user_id:
        room = f'user_{user_id}'
        leave_room(room)
        current_app.logger.info(f'User {user_id} explicitly left room {room}')


# --- Function to be called by the backend when an order status changes ---
# This is NOT a SocketIO event handler triggered by the client,
# but a helper function for the backend to push updates TO the client.
def broadcast_status_update(order_id, new_status):
    """Broadcasts an order status update to the relevant user's room."""
    try:
        order = db.session.get(Order, order_id)
        if order and order.customer: # Check if order and associated customer exist
            user_id = order.user_id
            room = f'user_{user_id}'
            current_app.logger.info(f"Broadcasting status update for order {order_id} to room {room}: {new_status}")
            socketio.emit('status_update',
                          {'order_id': order_id, 'status': new_status},
                          room=room)
        else:
             current_app.logger.warning(f"Could not broadcast status update for non-existent order or user: Order ID {order_id}")
    except Exception as e:
        current_app.logger.error(f"Error broadcasting status update for order {order_id}: {e}")

# Example of how an admin/restaurant backend might trigger an update:
# @some_admin_route(...)
# def update_order_status_route(order_id):
#     # ... logic to update order status in DB ...
#     order = Order.query.get(order_id)
#     order.status = "Preparing"
#     db.session.commit()
#     # Broadcast the change
#     broadcast_status_update(order_id, order.status)
#     return "Status updated"

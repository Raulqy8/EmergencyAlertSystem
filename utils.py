# utils.py  ← THIS IS THE FINAL VERSION
from flask_socketio import SocketIO

# We will set this later from app.py
socketio: SocketIO = None

def set_socketio_instance(instance: SocketIO):
    global socketio
    socketio = instance

def broadcast_new_alert(alert):
    from models.models import User
    data = {
        'alert_id': alert.alert_id,
        'type': alert.type or 'emergency',
        'severity': alert.severity or 'critical',
        'description': alert.description or 'Panic button pressed!',
        'status': alert.status,
        'latitude': float(alert.latitude) if alert.latitude else None,
        'longitude': float(alert.longitude) if alert.longitude else None,
        'timestamp': alert.timestamp.isoformat(),
        'citizen_name': alert.user.name if alert.user and hasattr(alert.user, 'name') else 'Anonymous'
    }
    if socketio:
        socketio.emit('new_alert', data, broadcast=True)
        print(f"BROADCASTED Alert #{alert.alert_id}")
    else:
        print("SocketIO not ready yet!")

def broadcast_status_update(alert_id, new_status):
    if socketio:
        socketio.emit('status_update', {'alert_id': alert_id, 'status': new_status}, broadcast=True)
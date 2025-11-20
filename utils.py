from flask_socketio import SocketIO

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
        'citizen_name': alert.user.name if alert.user else 'Anonymous',
        'assigned_to': alert.responder_id,
        'responder_name': alert.responder.name if alert.responder else None
    }
    if socketio:
        socketio.emit('new_alert', data)
        print(f"BROADCASTED Alert #{alert.alert_id} to all clients")
    else:
        print("SocketIO not initialized yet!")

def broadcast_status_update(alert_id, new_status, responder_name=None):
    if socketio:
        # Same fix here
        socketio.emit('status_update', {
            'alert_id': alert_id,
            'status': new_status,
            'responder_name': responder_name or 'Unknown'
        })  # ← FIXED — no broadcast=True
        print(f"Status update broadcasted: Alert #{alert_id} → {new_status}")
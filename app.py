# app.py  ← COPY-PASTE THIS ENTIRE FILE (replace yours)

# === 1. MONKEY PATCH FIRST — BEFORE ANYTHING ELSE! ===
import eventlet
eventlet.monkey_patch()          # ← THIS MUST BE THE VERY FIRST LINES

# === 2. NOW import everything else ===
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_required, current_user
from flask_socketio import SocketIO
from config import Config
from models.models import db, User, Alert
from routes.auth_routes import auth_bp
from routes.alert_routes import alert_bp
from routes.admin_routes import admin_bp
from routes.responder_routes import responder_bp
from utils import broadcast_new_alert, broadcast_status_update

# === 3. Create app ===
app = Flask(__name__)
app.config.from_object(Config)

# === 4. Init extensions ===
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

from utils import set_socketio_instance
set_socketio_instance(socketio)

# === 5. User loader ===
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === 6. Register blueprints ===
app.register_blueprint(auth_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(responder_bp)

# === 7. Routes ===
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('base.html')  # or create a landing page later

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif current_user.role in ['police', 'firefighter', 'medical']:
        return redirect(url_for('responder.responder_dashboard'))
    else:
        return redirect(url_for('alert.report_alert'))

# === 8. API for map ===
@app.route('/api/alerts/active')
@login_required
def api_active_alerts():
    if current_user.role != 'admin':
        return jsonify([])
    alerts = Alert.query.filter(Alert.status.in_(['reported', 'in_progress', 'on_route'])).all()
    return jsonify([{
        'alert_id': a.alert_id,
        'type': a.type,
        'severity': a.severity,
        'description': a.description,
        'status': a.status,
        'latitude': float(a.latitude) if a.latitude else None,
        'longitude': float(a.longitude) if a.longitude else None,
        'timestamp': a.timestamp.isoformat(),
        'user': {'name': a.user.name}
    } for a in alerts if a.latitude and a.longitude])

# === 9. Broadcast helpers ===


# === 10. SocketIO connect ===
@socketio.on('connect')
def handle_connect():
    print(f"User connected: {current_user if current_user.is_authenticated else 'Anonymous'}")

# Add this route somewhere (e.g. in admin_routes.py or app.py)
@app.route('/admin/responders')
@login_required
def get_responders():
    if current_user.role != 'admin':
        return jsonify([])
    responders = User.query.filter(User.role.in_(['police', 'firefighter', 'medical'])).all()
    return jsonify([{'user_id': u.user_id, 'name': u.name, 'role': u.role} for u in responders])

# === 11. RUN ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database ready")

    print("EMERGENCY SYSTEM LIVE")
    print("Panic Button → http://127.0.0.1:5000/alert/report")
    print("Admin Map     → http://127.0.0.1:5000/admin/dashboard")

    socketio.run(
        app,
        host='127.0.0.1',
        port=5000,
        debug=True,
        use_reloader=False   # REQUIRED on Windows
    )
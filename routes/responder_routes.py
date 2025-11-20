from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.models import db, Alert
from utils import broadcast_status_update

responder_bp = Blueprint('responder', __name__, url_prefix='/responder')

@responder_bp.route('/responder/dashboard')
@login_required
def responder_dashboard():
    return render_template('responder_dashboard.html')

@responder_bp.route('/api/my_alerts')
@login_required
def api_my_alerts():
    alerts = Alert.query.filter_by(responder_id=current_user.user_id)\
                         .filter(Alert.status != 'resolved')\
                         .all()
    return jsonify([{
        'alert_id': a.alert_id,
        'type': a.type,
        'severity': a.severity,
        'description': a.description,
        'status': a.status,
        'latitude': float(a.latitude),
        'longitude': float(a.longitude),
        'timestamp': a.timestamp.isoformat(),
        'citizen_name': a.user.name
    } for a in alerts])

@responder_bp.route('/set_status/<int:alert_id>/<string:new_status>', methods=['POST'])
@login_required
def set_status(alert_id, new_status):
    alert = Alert.query.get_or_404(alert_id)

    if alert.responder_id != current_user.user_id:
        flash('This is not your mission!')
        return redirect(url_for('responder.responder_dashboard'))

    if new_status not in ['on_route', 'on_site', 'resolved']:
        flash('Invalid status')
        return redirect(url_for('responder.responder_dashboard'))

    if alert.status == 'assigned' and new_status != 'on_route':
        flash('You must accept first (On Route)')
        return redirect(url_for('responder.responder_dashboard'))

    old_status = alert.status
    alert.status = new_status
    db.session.commit()

    broadcast_status_update(alert_id, new_status, current_user.name)
    flash(f'Status updated to {new_status.replace("_", " ")}')
    return redirect(url_for('responder.responder_dashboard'))
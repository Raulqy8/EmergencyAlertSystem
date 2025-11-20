from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.models import db, Alert
from utils import broadcast_new_alert

alert_bp = Blueprint('alert', __name__, url_prefix='/alert')

@alert_bp.route('/report')
@login_required
def report_alert():
    return render_template('report_alert.html')

@alert_bp.route('/report', methods=['POST'])
@login_required
def submit_alert():
    # Accept both HTML form and JSON (panic button)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    # sanitize type to match DB enum values
    allowed_types = ('fire', 'medical', 'crime', 'utility', 'other')
    t = (data.get('type') or 'other').lower()
    if t not in allowed_types:
        # map any unknown/legacy values (e.g. "emergency") to 'other'
        t = 'other'

    # sanitize severity
    allowed_severities = ('low', 'medium', 'high', 'critical')
    severity = (data.get('severity') or 'critical').lower()
    if severity not in allowed_severities:
        severity = 'critical'

    # parse coordinates safely
    def parse_float(v):
        try:
            return float(v) if v not in (None, '') else None
        except (TypeError, ValueError):
            return None

    latitude = parse_float(data.get('latitude'))
    longitude = parse_float(data.get('longitude'))

    description = data.get('description') or 'Panic button activated'

    new_alert = Alert(
        user_id=current_user.user_id,
        type=t,
        severity=severity,
        description=description,
        latitude=latitude,
        longitude=longitude,
        status='reported'
    )

    db.session.add(new_alert)
    db.session.commit()

    # Broadcast to connected clients (map etc.)
    try:
        broadcast_new_alert(new_alert)
    except Exception as e:
        print("Broadcast failed:", e)

    if request.is_json:
        return jsonify({'success': True, 'alert_id': new_alert.alert_id})
    flash("Alert submitted.", "success")
    return redirect(url_for('alert.report_alert'))

@alert_bp.route('/my-alerts')
@login_required
def view_alerts():
    alerts = Alert.query.filter_by(user_id=current_user.user_id).order_by(Alert.timestamp.desc()).all()
    return render_template('my_alerts.html', alerts=alerts)
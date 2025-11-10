from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, Alert, User

responder_bp = Blueprint('responder', __name__)

# Responder dashboard
@responder_bp.route('/responder/dashboard')
@login_required
def responder_dashboard():
    if current_user.role not in ['police', 'firefighter', 'medical']:
        flash("Access denied. Responders only.", "danger")
        return redirect(url_for('dashboard'))
    
    # For now, responders see all alerts marked 'in_progress'
    alerts = Alert.query.filter_by(status='in_progress').all()
    return render_template('responder_dashboard.html', alerts=alerts)

# Update alert status (on route, resolved)
@responder_bp.route('/responder/update/<int:alert_id>/<string:new_status>')
@login_required
def update_status(alert_id, new_status):
    if current_user.role not in ['police', 'firefighter', 'medical']:
        flash("Access denied.", "danger")
        return redirect(url_for('dashboard'))

    alert = Alert.query.get(alert_id)
    if alert:
        # Only responders should be able to update assigned alerts
        alert.status = new_status
        db.session.commit()
        flash(f"Alert #{alert.alert_id} updated to '{new_status}'.", "success")

    return redirect(url_for('responder.responder_dashboard'))

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.models import db, Alert, User
from utils import broadcast_new_alert, broadcast_status_update

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/dashboard')
@login_required

def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied. Admins only", "danger")
        return redirect(url_for('dashboard'))
    
    alerts = Alert.query.order_by(Alert.timestamp.desc()).all()
    responders = User.query.filter(User.role.in_(['police', 'firefighter', 'medical'])).all()
    return render_template('admin_dashboard.html', alerts = alerts, responders=responders)

@admin_bp.route('/admin/assign/<int:alert_id>', methods = ['POST'])
@login_required
def assign_responder(alert_id):
    if current_user.role != 'admin':
        flash('Access denied')
        return redirect(url_for('admin.admin_dashboard'))

    alert = Alert.query.get_or_404(alert_id)
    responder_id = request.form['responder_id']

    alert.responder_id = int(responder_id)
    alert.status = 'assigned'
    db.session.commit()

    responder = User.query.get(responder_id)
    broadcast_new_alert(alert)
    broadcast_status_update(alert_id, 'assigned', responder.name)

    flash('Responder assigned successfully!')
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/resolve/<int:alert_id>')
@login_required

def resolve_alert(alert_id):
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('admin.admin_dashboard'))
    
    alert = Alert.query.get(alert_id)
    if alert:
        alert.status = 'resolved'
        db.session.commit()
        flash(f"Alert #{alert.alert_id} marked as resolved.", "success")

    return redirect(url_for('admin.admin_dashboard'))


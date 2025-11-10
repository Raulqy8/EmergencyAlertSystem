from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.models import db, Alert, User

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
    if current_user != 'admin':
        flash("Access denied!","danger")
        return redirect(url_for('admin.admin_dashboard'))
    
    responder_id = request.form.get('responder_id')
    alert = Alert.query.get(alert_id)
    responder = User.query.get(responder_id)

    if alert and responder:
        alert.status = 'in_progress'
        db.session.commit()
        flash(f"Responder {responder.name} assigned to alert #{alert.alert_id}.", "success")
    else:
        flash("Assignment failed. Invalid alert or responder.", "danger")

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
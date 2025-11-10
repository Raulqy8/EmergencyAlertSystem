from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, Alert

alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/report', methods = ['GET', 'POST'])
@login_required

def report_alert():
    if request.method == 'POST':
        type_ = request.form['type']
        severity = request.form['severity']
        description = request.form['description']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        alert = Alert(
            user_id = current_user.user_id,
            type = type_,
            severity = severity,
            description = description,
            latitude = float(latitude) if latitude else None,
            longitude = float(longitude) if longitude else None,
            status= 'reported')
        
        db.session.add(alert)
        db.session.commit()

        flash("Emergency reported successfully!", "success")
        return redirect(url_for('alert.view_alerts'))
    
    return render_template('report_alert.html')


@alert_bp.route('/my-alerts')
@login_required

def view_alerts():
    alerts = Alert.query.filter_by(user_id = current_user.user_id).all()
    return render_template('my_alerts.html', alerts = alerts)
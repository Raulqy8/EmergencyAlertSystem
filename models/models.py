from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    role = db.Column(db.Enum('citizen', 'police', 'firefighter', 'medical', 'admin'))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    phone = db.Column(db.String(20))
    location = db.Column(db.String(255))
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.user_id)

    
class Alert(db.Model):
    __tablename__ = 'alerts'
    alert_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    responder_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    type = db.Column(db.Enum('fire', 'medical', 'crime', 'utility', 'other', 'emergency'))
    severity = db.Column(db.Enum('low', 'medium', 'high', 'critical'))
    description = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.Enum('reported', 'assigned', 'on_route', 'on_site', 'resolved', 'false_alarm'), default='reported')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], backref='alerts')
    responder = db.relationship('User', foreign_keys=[responder_id], backref='assigned_alerts')

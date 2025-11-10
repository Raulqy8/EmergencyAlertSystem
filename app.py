from flask import Flask, render_template
from flask_login import LoginManager, login_required, current_user
from config import Config
from models.models import db, User
from routes.auth_routes import auth_bp
from routes.alert_routes import alert_bp
from routes.admin_routes import admin_bp
from routes.responder_routes import responder_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

app.register_blueprint(auth_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(responder_bp)

@app.route('/')
def home():
    return "<h2>Emergency Alert System Connected to MariaDB 🚨</h2>"

@app.route('/dashboard')
@login_required
def dashboard():
    return f"<h3>Welcome, {current_user.name}! You are logged in as {current_user.role}.</h3>"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


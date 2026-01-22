import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, Admin, User, Product, Sale

# -------- FLASK SETUP --------
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///coffee_manager.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db.init_app(app)

# -------- LOGIN MANAGER --------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))  # Only admins for now

# -------- BLUEPRINTS --------
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.costs import costs_bp
from routes.products import products_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(costs_bp)
app.register_blueprint(products_bp)

# -------- ROOT ROUTE --------
@app.route("/")
def home():
    return redirect(url_for("dashboard.dashboard"))

# -------- INIT DB & CREATE DEFAULT ADMINS --------
with app.app_context():
    db.create_all()

    # List of default admins
    default_admins = [
        {"username": "admin1", "password": "pass123", "full_name": "Alice"},
        {"username": "admin2", "password": "pass456", "full_name": "Bob"},
        {"username": "admin3", "password": "pass789", "full_name": "Charlie"},
    ]

    for adm in default_admins:
        if not Admin.query.filter_by(username=adm["username"]).first():
            admin = Admin(username=adm["username"], full_name=adm["full_name"])
            admin.set_password(adm["password"])
            db.session.add(admin)
    db.session.commit()
    print("Default admins created!")

# -------- RUN --------
if __name__ == "__main__":
    # Use 0.0.0.0 on Render for external access
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

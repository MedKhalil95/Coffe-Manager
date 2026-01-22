# app.py - Fixed version
import os
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from models import db, Admin, Product, Sale, FixedCost  # Removed User and Ingredient imports

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
    return Admin.query.get(int(user_id))

# -------- BLUEPRINTS --------
# app.py - Correct import order


# ... config code ..

# Import models AFTER app is created

# Import blueprints AFTER models
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.costs import costs_bp
from routes.products import products_bp

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(costs_bp)  # <-- THIS LINE MUST EXIST
app.register_blueprint(products_bp)
# -------- ROOT ROUTE --------
@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("auth.login"))
# Add this to app.py (temporarily)
@app.route('/costs')
def direct_costs():
    """Direct route to costs for testing"""
    return redirect(url_for('costs.list_costs'))
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
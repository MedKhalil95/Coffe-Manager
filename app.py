from flask import Flask, app, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required
from models import db, User, Product, Sale

from models import db, Admin
import os
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///coffee_manager.db"
)

# -------- FLASK SETUP --------


db.init_app(app)

# -------- LOGIN MANAGER --------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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


# -------- INIT DB & CREATE ADM
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
    app.run(debug=True)

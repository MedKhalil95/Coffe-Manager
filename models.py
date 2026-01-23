# models.py - Updated with unit_price and quantity fields
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

# -------- ADMIN USER --------
class Admin(UserMixin, db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(150))
    
    # Relationships
    products = db.relationship('Product', backref='admin', lazy=True)
    sales = db.relationship('Sale', backref='admin', lazy=True)
    fixed_costs = db.relationship('FixedCost', backref='admin', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# -------- PRODUCT --------
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True)
    sell_price = db.Column(db.Float, nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, default=1)
    
    # relationship to sales
    sales = db.relationship('Sale', backref='product', lazy=True)

# -------- SALE --------
class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, default=1)

# -------- FIXED COST --------
class FixedCost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price per unit
    quantity = db.Column(db.Float, nullable=False, default=1)  # Number of units
    category = db.Column(db.String(100), nullable=False, default='General')
    date = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, default=1)
    
    # Property to calculate total amount
    @property
    def total_amount(self):
        return self.unit_price * self.quantity
# app.py
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, Product, Order, OrderItem, User, Purchase, Employee, SalaryPayment
import stripe
from datetime import datetime
from sqlalchemy import extract
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coffee.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your-secret-key-here-change-this"

db.init_app(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Stripe test key
stripe.api_key = "sk_test_YOUR_SECRET_KEY"

# ✅ FLASK 3.x SAFE INITIALIZATION
# app.py - Update the initialization section
# app.py - Update the initialization section
with app.app_context():
    db.create_all()
    
    # Create multiple admin users if not exists
    admins = [
        {'username': 'admin1', 'password': 'admin123', 'is_admin': True},
        {'username': 'admin2', 'password': 'admin456', 'is_admin': True},
        {'username': 'admin3', 'password': 'admin789', 'is_admin': True},
        {'username': 'cashier1', 'password': 'cash123', 'is_admin': False},
    ]
    
    for admin_data in admins:
        if User.query.filter_by(username=admin_data['username']).first() is None:
            user = User(username=admin_data['username'], is_admin=admin_data['is_admin'])
            user.set_password(admin_data['password'])
            db.session.add(user)
    
    # Create sample products for each admin (keep generic names)
    if Product.query.count() == 0:
        # Get all admin users
        admin_users = User.query.filter_by(is_admin=True).all()
        
        for admin in admin_users:
            db.session.add_all([
                Product(name="Espresso", price=3.5, stock=50, 
                       cost_price=1.0, admin_id=admin.id),
                Product(name="Cappuccino", price=4.5, stock=40, 
                       cost_price=1.2, admin_id=admin.id),
                Product(name="Latte", price=5.0, stock=30, 
                       cost_price=1.5, admin_id=admin.id),
            ])
        db.session.commit()
        # ---------------- AUTHENTICATION ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            if user.is_admin:
                return redirect(url_for("admin_dashboard"))
            else:
                return redirect(url_for("pos"))
        else:
            flash("Invalid credentials")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# app.py - Update routes to filter by current admin

# ---------------- POS ----------------
@app.route("/")
@login_required
def pos():
    if current_user.is_admin:
        # Admins see only their products
        products = Product.query.filter_by(admin_id=current_user.id).all()
    else:
        # Non-admins see all products (if needed)
        products = Product.query.all()
    return render_template("pos.html", products=products)

# ---------------- ADMIN DASHBOARD ----------------
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    # Only show current admin's products
    products = Product.query.filter_by(admin_id=current_user.id).all()
    
    # Only show current admin's orders
    orders = Order.query.filter_by(admin_id=current_user.id, paid=True).all()
    
    # Calculate revenue statistics for this admin only
    total_revenue = sum(order.total for order in orders)
    total_orders = len(orders)
    
    # Calculate profit for this admin only
    total_cost = 0
    for product in products:
        # Get purchases for this admin only
        admin_purchases = Purchase.query.filter_by(
            product_id=product.id, 
            admin_id=current_user.id
        ).all()
        purchased_qty = sum(p.quantity for p in admin_purchases)
        sold_qty = purchased_qty - product.stock
        total_cost += sold_qty * (product.cost_price or 0)
    
    total_profit = total_revenue - total_cost
    
    return render_template("admin_dashboard.html", 
                         products=products,
                         total_revenue=total_revenue,
                         total_orders=total_orders,
                         total_profit=total_profit)

# ---------------- PRODUCT MANAGEMENT ----------------
@app.route("/admin/products", methods=["GET", "POST"])
@login_required
def manage_products():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    if request.method == "POST":
        product_id = request.form.get("product_id")
        
        if product_id:  # Update existing product
            product = Product.query.get(product_id)
            # Verify admin owns this product
            if product.admin_id != current_user.id:
                flash("Access denied")
                return redirect(url_for("manage_products"))
            
            product.name = request.form["name"]
            product.price = float(request.form["price"])
            product.cost_price = float(request.form.get("cost_price", 0))
            db.session.commit()
            flash("Product updated successfully")
        else:  # Add new product
            product = Product(
                name=request.form["name"],
                price=float(request.form["price"]),
                stock=int(request.form.get("stock", 0)),
                cost_price=float(request.form.get("cost_price", 0)),
                admin_id=current_user.id  # Assign to current admin
            )
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully")
        
        return redirect(url_for("manage_products"))
    
    # Only show current admin's products
    products = Product.query.filter_by(admin_id=current_user.id).all()
    return render_template("manage_products.html", products=products)

@app.route("/admin/products/delete/<int:id>")
@login_required
def delete_product(id):
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    product = Product.query.get_or_404(id)
    
    # Verify admin owns this product
    if product.admin_id != current_user.id:
        flash("Access denied")
        return redirect(url_for("manage_products"))
    
    db.session.delete(product)
    db.session.commit()
    flash("Product deleted")
    return redirect(url_for("manage_products"))

# ---------------- PURCHASE MANAGEMENT ----------------
@app.route("/admin/purchases", methods=["GET", "POST"])
@login_required
def manage_purchases():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    if request.method == "POST":
        product_id = request.form["product_id"]
        quantity = int(request.form["quantity"])
        unit_cost = float(request.form["unit_cost"])
        
        product = Product.query.get(product_id)
        
        # Verify admin owns this product
        if product.admin_id != current_user.id:
            flash("Access denied")
            return redirect(url_for("manage_purchases"))
        
        # Update product stock and purchase records
        product.stock += quantity
        product.purchased_quantity += quantity
        product.cost_price = unit_cost
        
        # Record the purchase with admin_id
        purchase = Purchase(
            product_id=product_id,
            quantity=quantity,
            unit_cost=unit_cost,
            total_cost=quantity * unit_cost,
            admin_id=current_user.id  # Track which admin made purchase
        )
        db.session.add(purchase)
        db.session.commit()
        
        flash("Purchase recorded successfully")
        return redirect(url_for("manage_purchases"))
    
    # Only show current admin's products for purchase
    products = Product.query.filter_by(admin_id=current_user.id).all()
    
    # Only show current admin's purchase history
    purchases = Purchase.query.filter_by(admin_id=current_user.id).order_by(
        Purchase.purchase_date.desc()
    ).all()
    
    return render_template("manage_purchases.html", products=products, purchases=purchases)

# ---------------- INVENTORY ----------------
@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    if request.method == "POST":
        product_id = request.form["product_id"]
        stock = request.form["stock"]
        product = Product.query.get(product_id)
        
        # Verify admin owns this product
        if product.admin_id != current_user.id:
            flash("Access denied")
            return redirect(url_for("inventory"))
        
        product.stock = int(stock)
        db.session.commit()
        return redirect("/inventory")

    # Only show current admin's products
    products = Product.query.filter_by(admin_id=current_user.id).all()
    return render_template("inventory.html", products=products)

# ---------------- ORDER CREATION ----------------
@app.route("/order", methods=["POST"])
@login_required
def create_order():
    data = request.json
    order = Order(total=0, admin_id=current_user.id)  # Track which admin created order
    db.session.add(order)
    db.session.commit()

    total = 0
    for item in data:
        product = Product.query.get(item["id"])
        
        # Verify product belongs to current admin (for admin users)
        if current_user.is_admin and product.admin_id != current_user.id:
            return jsonify({"error": "Access denied to product"}), 403

        if product.stock < item["qty"]:
            return jsonify({"error": f"{product.name} out of stock"}), 400

        product.stock -= item["qty"]
        subtotal = product.price * item["qty"]
        total += subtotal

        db.session.add(OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item["qty"]
        ))

    order.total = total
    db.session.commit()

    return jsonify({"order_id": order.id, "total": total})
# app.py - Add these imports a

# app.py - Add these routes after the existing routes

# ---------------- EMPLOYEE MANAGEMENT ----------------
@app.route("/admin/employees", methods=["GET", "POST"])
@login_required
def manage_employees():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    if request.method == "POST":
        employee_id = request.form.get("employee_id")
        
        if employee_id:  # Update existing employee
            employee = Employee.query.get(employee_id)
            if employee.admin_id != current_user.id:
                flash("Access denied")
                return redirect(url_for("manage_employees"))
            
            employee.name = request.form["name"]
            employee.position = request.form["position"]
            employee.monthly_salary = float(request.form["monthly_salary"])
            db.session.commit()
            flash("Employee updated successfully")
        else:  # Add new employee
            employee = Employee(
                name=request.form["name"],
                position=request.form["position"],
                monthly_salary=float(request.form["monthly_salary"]),
                admin_id=current_user.id
            )
            db.session.add(employee)
            db.session.commit()
            flash("Employee added successfully")
        
        return redirect(url_for("manage_employees"))
    
    # Get current month/year for report
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    employees = Employee.query.filter_by(admin_id=current_user.id).all()
    salary_payments = SalaryPayment.query.filter_by(
        admin_id=current_user.id
    ).order_by(SalaryPayment.payment_date.desc()).limit(20).all()
    
    return render_template("employees.html", 
                         employees=employees,
                         salary_payments=salary_payments,
                         current_month=current_month,
                         current_year=current_year)

@app.route("/admin/employees/delete/<int:id>")
@login_required
def delete_employee(id):
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    employee = Employee.query.get_or_404(id)
    
    if employee.admin_id != current_user.id:
        flash("Access denied")
        return redirect(url_for("employees"))
    
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted")
    return redirect(url_for("manage_employees"))

@app.route("/admin/employees/pay/<int:employee_id>")
@login_required
def pay_salary(employee_id):
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    employee = Employee.query.get_or_404(employee_id)
    
    if employee.admin_id != current_user.id:
        flash("Access denied")
        return redirect(url_for("manage_employees"))
    
    now = datetime.now()
    
    # Check if already paid this month
    existing_payment = SalaryPayment.query.filter_by(
        employee_id=employee_id,
        month=now.month,
        year=now.year,
        admin_id=current_user.id
    ).first()
    
    if existing_payment:
        flash("Salary already paid for this month")
    else:
        salary_payment = SalaryPayment(
            employee_id=employee_id,
            amount=employee.monthly_salary,
            month=now.month,
            year=now.year,
            admin_id=current_user.id
        )
        db.session.add(salary_payment)
        db.session.commit()
        flash(f"Salary of ${employee.monthly_salary} paid for {employee.name}")
    
    return redirect(url_for("manage_employees"))

# ---------------- MONTHLY FINANCIAL REPORT ----------------
@app.route("/admin/financial-report")
@login_required
def monthly_financial_report():
    if not current_user.is_admin:
        return redirect(url_for("pos"))
    
    # Get month/year from query parameters or use current month
    month = request.args.get('month', type=int, default=datetime.now().month)
    year = request.args.get('year', type=int, default=datetime.now().year)
    
    # Calculate revenue from orders for the specific month
    orders = Order.query.filter(
        Order.admin_id == current_user.id,
        Order.paid == True,
        extract('month', Order.created_at) == month,
        extract('year', Order.created_at) == year
    ).all()
    
    total_revenue = sum(order.total for order in orders)
    order_count = len(orders)
    
    # Calculate cost of goods sold for the month
    total_cost = 0
    products = Product.query.filter_by(admin_id=current_user.id).all()
    
    for product in products:
        # Get purchases for this admin and month
        monthly_purchases = Purchase.query.filter(
            Purchase.admin_id == current_user.id,
            Purchase.product_id == product.id,
            extract('month', Purchase.purchase_date) == month,
            extract('year', Purchase.purchase_date) == year
        ).all()
        
        purchased_qty = sum(p.quantity for p in monthly_purchases)
        total_cost += purchased_qty * (product.cost_price or 0)
    
    # Calculate total salaries for the month
    monthly_salary_payments = SalaryPayment.query.filter(
        SalaryPayment.admin_id == current_user.id,
        SalaryPayment.month == month,
        SalaryPayment.year == year
    ).all()
    
    total_salaries = sum(payment.amount for payment in monthly_salary_payments)
    
    # Calculate profits
    gross_profit = total_revenue - total_cost
    net_profit = gross_profit - total_salaries
    
    report_data = {
        'total_revenue': total_revenue,
        'total_cost': total_cost,
        'total_salaries': total_salaries,
        'gross_profit': gross_profit,
        'net_profit': net_profit,
        'order_count': order_count
    }
    
    # Get data for template
    employees = Employee.query.filter_by(admin_id=current_user.id).all()
    salary_payments = SalaryPayment.query.filter_by(
        admin_id=current_user.id
    ).order_by(SalaryPayment.payment_date.desc()).all()
    
    return render_template("employees.html",
                         report_data=report_data,
                         selected_month=month,
                         current_year=year,
                         employees=employees,
                         salary_payments=salary_payments)

# app.py - Update the initi
# ---------------- STRIPE ----------------
@app.route("/pay/<int:order_id>")
@login_required
def pay(order_id):
    order = Order.query.get_or_404(order_id)

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {"name": f"Coffee Order #{order.id}"},
                "unit_amount": int(order.total * 100),
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=url_for("payment_success", order_id=order_id, _external=True),
        cancel_url=url_for("pos", _external=True),
    )

    return redirect(session.url)

@app.route("/payment_success/<int:order_id>")
def payment_success(order_id):
    order = Order.query.get_or_404(order_id)
    order.paid = True
    db.session.commit()
    return render_template("payment_success.html")

if __name__ == "__main__":
    app.run(debug=True)
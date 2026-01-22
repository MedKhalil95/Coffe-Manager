# routes/dashboard.py - Simplified version
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import db, Product, Sale, FixedCost
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    admin_id = current_user.id
    
    # Get all data for current admin
    products = Product.query.filter_by(admin_id=admin_id).all()
    sales = Sale.query.filter_by(admin_id=admin_id).all()
    fixed_costs = FixedCost.query.filter_by(admin_id=admin_id).all()
    
    # Calculate total revenue
    total_sales = sum(sale.quantity * sale.product.sell_price for sale in sales)
    
    # Simplified: Assume fixed cost per product is 30% of sell price
    # You can adjust this as needed
    total_product_costs = sum(sale.quantity * (sale.product.sell_price * 0.3) for sale in sales)
    
    # Total fixed costs
    total_fixed_costs = sum(cost.amount for cost in fixed_costs)
    
    total_costs = total_product_costs + total_fixed_costs
    net_profit = total_sales - total_costs
    
    # Prepare products overview
    products_data = []
    for product in products:
        total_sold = sum(s.quantity for s in product.sales if s.admin_id == admin_id)
        cost_per_product = product.sell_price * 0.3  # 30% cost assumption
        
        products_data.append({
            'name': product.name,
            'total_sold': total_sold,
            'sell_price': product.sell_price,
            'cost_per_product': cost_per_product
        })
    
    # Simple chart data
    chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    chart_values = [1000, 1200, 800, 1500, 2000, 1800]
    
    return render_template('dashboard.html',
                         total_sales=total_sales,
                         total_costs=total_costs,
                         total_fixed_costs=total_fixed_costs,
                         net_profit=net_profit,
                         chart_data={'labels': chart_labels, 'values': chart_values},
                         products=products_data)
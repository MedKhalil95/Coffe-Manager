# routes/dashboard.py - Updated version without cost per product coefficient
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
    
    # Calculate total revenue (all sales)
    total_sales = sum(sale.quantity * sale.product.sell_price for sale in sales)
    
    # Total fixed costs (only actual recorded costs)
    # In dashboard.py, update the costs calculation:
# Total fixed costs (using the new calculation)
    total_fixed_costs = sum(cost.unit_price * cost.quantity for cost in fixed_costs)
    
    # Total costs = only fixed costs (no product cost coefficient)
    total_costs = total_fixed_costs
    
    # Net profit = total sales - total fixed costs
    net_profit = total_sales - total_costs
    
    # Prepare products overview - WITHOUT cost per product
    products_data = []
    for product in products:
        total_sold = sum(s.quantity for s in product.sales if s.admin_id == admin_id)
        
        products_data.append({
            'name': product.name,
            'total_sold': total_sold,
            'sell_price': product.sell_price,
            # Remove cost_per_product since we don't use it anymore
        })
    
    # Simple chart data (last 6 months profit)
    # For simplicity, using static data - you can implement actual monthly data later
    chart_labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    chart_values = [1000, 1200, 800, 1500, 2000, 1800]
    
    return render_template('dashboard.html',
                         total_sales=total_sales,
                         total_costs=total_costs,
                         total_fixed_costs=total_fixed_costs,
                         net_profit=net_profit,
                         chart_data={'labels': chart_labels, 'values': chart_values},
                         products=products_data)
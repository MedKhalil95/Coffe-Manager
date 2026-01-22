from flask import Blueprint, render_template
from flask_login import login_required
from models import Product, Sale, FixedCost

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@login_required
@dashboard_bp.route("/")
def dashboard():
    products = Product.query.all()

    # ---- Calculate total sold units per product ----
    for p in products:
        p.total_sold = sum(s.quantity for s in p.sales) if p.sales else 0

        # Cost per product = sum of ingredient costs
        p.cost_per_product = sum(
            pi.qty_used * pi.ingredient.unit_cost for pi in p.recipe
        ) if p.recipe else 0

    # ---- Total revenue ----
    total_sales = sum(p.total_sold * p.sell_price for p in products)

    # ---- Total cost from recipe ----
    total_product_cost = sum(p.total_sold * p.cost_per_product for p in products)

    # ---- Total fixed costs ----
    fixed_costs = FixedCost.query.all()
    total_fixed_costs = sum(c.amount for c in fixed_costs)

    # ---- Net profit ----
    net_profit = total_sales - (total_product_cost + total_fixed_costs)

    # ---- Chart data example for last 12 months ----
    # (Simplified example: months 1-12, random demo values)
    chart_data = {
        "labels": [f"Month {i}" for i in range(1, 13)],
        "values": [total_sales/12]*12  # Replace with real per-month calculation
    }

    return render_template(
        "dashboard.html",
        products=products,
        total_sales=total_sales,
        total_costs=total_product_cost + total_fixed_costs,
        net_profit=net_profit,
        chart_data=chart_data
    )

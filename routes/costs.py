# routes/costs.py - Updated with unit_price and quantity
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, FixedCost
from datetime import datetime

# Create blueprint
costs_bp = Blueprint('costs', __name__)

# Predefined categories
COST_CATEGORIES = ['Rent', 'Utilities', 'Salaries', 'Supplies', 'Raw Materials', 
                   'Packaging', 'Marketing', 'Maintenance', 'Insurance', 'Taxes', 
                   'Shipping', 'Office Supplies', 'Equipment', 'Software', 'General']

@costs_bp.route('/costs', methods=['GET', 'POST'])
@login_required
def list_costs():
    if request.method == 'POST':
        # Handle form submission for adding new cost
        name = request.form.get('name')
        unit_price = request.form.get('unit_price')
        quantity = request.form.get('quantity', 1)
        category = request.form.get('category', 'General')
        
        if not name or not unit_price:
            flash('Please fill in all required fields', 'danger')
        else:
            try:
                cost = FixedCost(
                    name=name,
                    unit_price=float(unit_price),
                    quantity=float(quantity),
                    category=category,
                    admin_id=current_user.id,
                    date=datetime.utcnow()
                )
                db.session.add(cost)
                db.session.commit()
                flash(f'Cost "{name}" added successfully!', 'success')
            except ValueError:
                flash('Invalid price or quantity entered', 'danger')
            
            return redirect(url_for('costs.list_costs'))
    
    # GET request - show the form and list of costs
    fixed_costs = FixedCost.query.filter_by(admin_id=current_user.id)\
                                 .order_by(FixedCost.category, FixedCost.date.desc())\
                                 .all()
    
    # Calculate totals
    category_totals = {}
    total_all_costs = 0
    
    for cost in fixed_costs:
        total_cost = cost.total_amount
        total_all_costs += total_cost
        
        if cost.category not in category_totals:
            category_totals[cost.category] = 0
        category_totals[cost.category] += total_cost
    
    return render_template('costs.html', 
                         fixed_costs=fixed_costs,
                         categories=COST_CATEGORIES,
                         category_totals=category_totals,
                         total_all_costs=total_all_costs)

@costs_bp.route('/costs/edit/<int:cost_id>', methods=['GET', 'POST'])
@login_required
def edit_cost(cost_id):
    cost = FixedCost.query.filter_by(id=cost_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        cost.name = request.form.get('name')
        cost.category = request.form.get('category', 'General')
        try:
            cost.unit_price = float(request.form.get('unit_price', 0))
            cost.quantity = float(request.form.get('quantity', 1))
            db.session.commit()
            flash('Cost updated successfully!', 'success')
            return redirect(url_for('costs.list_costs'))
        except ValueError:
            flash('Invalid price or quantity', 'danger')
    
    return render_template('edit_cost.html', 
                         cost=cost,
                         categories=COST_CATEGORIES)

@costs_bp.route('/costs/delete/<int:cost_id>')
@login_required
def delete_cost(cost_id):
    cost = FixedCost.query.filter_by(id=cost_id, admin_id=current_user.id).first_or_404()
    
    try:
        cost_name = cost.name
        db.session.delete(cost)
        db.session.commit()
        flash(f'Cost "{cost_name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting cost: {str(e)}', 'danger')
    
    return redirect(url_for('costs.list_costs'))
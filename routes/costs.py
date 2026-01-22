# routes/costs.py - CORRECTED VERSION
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, FixedCost
from datetime import datetime

# Create blueprint - make sure this matches what's in app.py
costs_bp = Blueprint('costs', __name__)

# This route handles BOTH displaying the form (GET) and processing it (POST)
@costs_bp.route('/costs', methods=['GET', 'POST'])
@login_required
def list_costs():
    if request.method == 'POST':
        # Handle form submission for adding new cost
        name = request.form.get('name')
        amount = request.form.get('amount')
        
        if not name or not amount:
            flash('Please fill in all fields', 'danger')
        else:
            try:
                cost = FixedCost(
                    name=name,
                    amount=float(amount),
                    admin_id=current_user.id,
                    date=datetime.utcnow()
                )
                db.session.add(cost)
                db.session.commit()
                flash(f'Cost "{name}" added successfully!', 'success')
            except ValueError:
                flash('Invalid amount entered', 'danger')
            
            return redirect(url_for('costs.list_costs'))
    
    # GET request - show the form and list of costs
    fixed_costs = FixedCost.query.filter_by(admin_id=current_user.id)\
                                 .order_by(FixedCost.date.desc())\
                                 .all()
    return render_template('costs.html', fixed_costs=fixed_costs)

# Edit cost - this should be a different route
@costs_bp.route('/costs/edit/<int:cost_id>', methods=['GET', 'POST'])
@login_required
def edit_cost(cost_id):
    cost = FixedCost.query.filter_by(id=cost_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        cost.name = request.form.get('name')
        try:
            cost.amount = float(request.form.get('amount', 0))
            db.session.commit()
            flash('Cost updated successfully!', 'success')
            return redirect(url_for('costs.list_costs'))
        except ValueError:
            flash('Invalid amount', 'danger')
    
    return render_template('edit_cost.html', cost=cost)

# Delete cost
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
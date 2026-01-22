from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, FixedCost
from datetime import datetime

costs_bp = Blueprint("costs", __name__, url_prefix="/costs")

# -------- LIST & ADD FIXED COSTS --------
@costs_bp.route("/", methods=["GET", "POST"])
@login_required
def list_costs():
    if request.method == "POST":
        name = request.form["name"]
        amount = float(request.form["amount"])
        cost = FixedCost(name=name, amount=amount, date=datetime.today())
        db.session.add(cost)
        db.session.commit()
        flash(f"Cost '{name}' added successfully!", "success")
        return redirect(url_for("costs.list_costs"))

    fixed_costs = FixedCost.query.order_by(FixedCost.date.desc()).all()
    return render_template("costs.html", fixed_costs=fixed_costs)

# -------- EDIT FIXED COST --------
@costs_bp.route("/edit/<int:cost_id>", methods=["GET", "POST"])
@login_required
def edit_cost(cost_id):
    cost = FixedCost.query.get_or_404(cost_id)
    if request.method == "POST":
        cost.name = request.form["name"]
        cost.amount = float(request.form["amount"])
        db.session.commit()
        flash(f"Cost '{cost.name}' updated successfully!", "success")
        return redirect(url_for("costs.list_costs"))
    return render_template("edit_cost.html", cost=cost)

# -------- DELETE FIXED COST --------
@costs_bp.route("/delete/<int:cost_id>")
@login_required
def delete_cost(cost_id):
    cost = FixedCost.query.get_or_404(cost_id)
    db.session.delete(cost)
    db.session.commit()
    flash(f"Cost '{cost.name}' deleted!", "danger")
    return redirect(url_for("costs.list_costs"))

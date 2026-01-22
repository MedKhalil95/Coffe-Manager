from flask import Blueprint, request, redirect
from flask_login import login_required
from models import Sale, ProductIngredient, Ingredient, db

sales_bp = Blueprint("sales", __name__)

@sales_bp.route("/add-sale", methods=["POST"])
@login_required
def add_sale():
    product_id = int(request.form["product_id"])
    qty = int(request.form["quantity"])

    sale = Sale(product_id=product_id, quantity=qty)
    db.session.add(sale)

    # auto decrease stock
    for pi in ProductIngredient.query.filter_by(product_id=product_id):
        ingredient = Ingredient.query.get(pi.ingredient_id)
        ingredient.stock_qty -= pi.qty_used * qty

    db.session.commit()
    return redirect("/dashboard")

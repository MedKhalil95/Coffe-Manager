from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import db, Product, Ingredient, ProductIngredient, Sale

products_bp = Blueprint("products", __name__, url_prefix="/products")

# -------- LIST PRODUCTS --------
@products_bp.route("/")
@login_required
def list_products():
    products = Product.query.all()

    # Calculate total sold
    for p in products:
        sold = sum(s.quantity for s in p.sales) if p.sales else 0
        p.total_sold = sold

    return render_template("products.html", products=products)

# -------- ADD PRODUCT --------
@products_bp.route("/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form["name"]
        sell_price = float(request.form["sell_price"])
        product = Product(name=name, sell_price=sell_price)
        db.session.add(product)
        db.session.commit()
        flash(f"Product '{name}' added successfully!", "success")
        return redirect(url_for("products.list_products"))
    return render_template("add_product.html")

# -------- EDIT PRODUCT --------
@products_bp.route("/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        product.name = request.form["name"]
        product.sell_price = float(request.form["sell_price"])
        db.session.commit()
        flash(f"Product '{product.name}' updated successfully!", "success")
        return redirect(url_for("products.list_products"))
    return render_template("edit_product.html", product=product)

# -------- DELETE PRODUCT --------
@products_bp.route("/delete/<int:product_id>")
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f"Product '{product.name}' deleted!", "danger")
    return redirect(url_for("products.list_products"))

# -------- PRODUCT RECIPE (INGREDIENT USAGE) --------
@products_bp.route("/recipe/<int:product_id>", methods=["GET", "POST"])
@login_required
def product_recipe(product_id):
    product = Product.query.get_or_404(product_id)
    ingredients = Ingredient.query.all()

    if request.method == "POST":
        ingredient_id = int(request.form["ingredient_id"])
        qty_used = float(request.form["qty_used"])

        # Update if already exists
        existing = ProductIngredient.query.filter_by(
            product_id=product.id, ingredient_id=ingredient_id
        ).first()
        if existing:
            existing.qty_used = qty_used
        else:
            pi = ProductIngredient(
                product_id=product.id,
                ingredient_id=ingredient_id,
                qty_used=qty_used
            )
            db.session.add(pi)
        db.session.commit()
        flash("Ingredient added/updated successfully!", "success")
        return redirect(url_for("products.product_recipe", product_id=product.id))

    recipe = ProductIngredient.query.filter_by(product_id=product.id).all()
    return render_template(
        "product_recipe.html",
        product=product,
        ingredients=ingredients,
        recipe=recipe
    )

# -------- RECORD SALES --------
@products_bp.route("/sale/<int:product_id>", methods=["GET", "POST"])
@login_required
def add_sale(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == "POST":
        quantity = int(request.form["quantity"])
        sale = Sale(product_id=product.id, quantity=quantity)
        db.session.add(sale)
        db.session.commit()
        flash(f"Recorded sale of {quantity} {product.name}(s).", "success")
        return redirect(url_for("products.list_products"))

    return render_template("add_sale.html", product=product)

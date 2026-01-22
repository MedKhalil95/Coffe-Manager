# routes/products.py - Simplified version
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Product, Sale
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
@login_required
def list_products():
    admin_id = current_user.id
    products = Product.query.filter_by(admin_id=admin_id).all()
    
    for product in products:
        product.total_sold = sum(s.quantity for s in product.sales if s.admin_id == admin_id)
    
    return render_template('products.html', products=products)

@products_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        sell_price = float(request.form['sell_price'])
        
        # Check if product already exists for this admin
        existing = Product.query.filter_by(name=name, admin_id=current_user.id).first()
        if existing:
            flash('Product already exists!', 'danger')
            return redirect(url_for('products.add_product'))
        
        product = Product(
            name=name,
            sell_price=sell_price,
            admin_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Product added!', 'success')
        return redirect(url_for('products.list_products'))
    
    return render_template('add_product.html')

@products_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        product.name = request.form['name']
        product.sell_price = float(request.form['sell_price'])
        db.session.commit()
        flash('Product updated!', 'success')
        return redirect(url_for('products.list_products'))
    
    return render_template('edit_product.html', product=product)

@products_bp.route('/products/<int:product_id>/delete')
@login_required
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, admin_id=current_user.id).first_or_404()
    
    # Delete related sales
    Sale.query.filter_by(product_id=product_id, admin_id=current_user.id).delete()
    
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted!', 'success')
    return redirect(url_for('products.list_products'))

@products_bp.route('/products/<int:product_id>/sale', methods=['GET', 'POST'])
@login_required
def add_sale(product_id):
    product = Product.query.filter_by(id=product_id, admin_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        
        sale = Sale(
            product_id=product_id,
            quantity=quantity,
            admin_id=current_user.id
        )
        db.session.add(sale)
        db.session.commit()
        flash(f'Sale of {quantity} {product.name}(s) recorded!', 'success')
        return redirect(url_for('products.list_products'))
    
    return render_template('add_sale.html', product=product)
from app import app, db, load_user
from app.models import User, Order, Admin, Reseller, Product, Item
from app.forms import SignUpForm, SignInForm, CreateOrderForm, ProductForm
from flask import render_template, redirect, url_for, request, flash, session
from flask_login import login_required, login_user, logout_user, current_user
import bcrypt
from datetime import datetime

@app.route('/')
@app.route('/index')
@app.route('/index.html')
def index(): 
    return render_template('index.html')

@app.route('/users/signin', methods=['GET', 'POST'])
def users_signin():
    form = SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first() # get first user with matching email
        if user.type == 'admin':
            if user and bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.passwd.encode('utf-8')): # admin check to work with seeded user
                login_user(user)
                return redirect(url_for('orders_admin'))
        if user and bcrypt.checkpw(form.passwd.data.encode('utf-8'), user.passwd): # check if user exists and password matches
            login_user(user)
            print(user.type)
            return redirect(url_for('orders'))
        else: # if user doesn't exist or password doesn't match
            flash('Invalid email or password') # flash error message
            return redirect(url_for('index')) # redirect to index page
    return render_template('users_signin.html', form=form)

@app.route('/users/signup', methods=['GET', 'POST'])
def users_signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user: # check if user exists, if so, flash error message
            flash('Email already in use')
            return render_template('users_signup.html', form=form)
        
        if form.passwd.data != form.passwd_confirm.data: # check if passwords match, if not, flash error message
            flash('Passwords do not match')
            return render_template('users_signup.html', form=form)
        
        salt = bcrypt.gensalt()
        passwd_hashed = bcrypt.hashpw(form.passwd.data.encode('utf-8'), salt)
        new_user = Reseller(
            email=form.email.data,
            company=form.company.data,
            address=form.address.data,
            phone=form.phone.data,
            website=form.website.data,
            passwd=passwd_hashed,
            type='reseller'
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('users_signup.html', form=form)

@app.route('/users/signout', methods=['GET', 'POST'])
@login_required
def users_signout():
    logout_user()
    session.pop('order_data', None)
    session.pop('items', None)
    flash('You have been logged out')
    return redirect(url_for('index'))

@app.route('/orders')
@login_required
def orders(): 
    user_orders = Order.query.filter_by(user_email=current_user.email).all()
    return render_template("orders.html", user=current_user, orders=user_orders)

@app.route('/orders/admin')
def orders_admin():
    orders = Order.query.all()
    return render_template("orders_admin.html", orders=orders)

# update order status admin only
@app.route('/orders/<number>/update', methods=['GET','POST'])
def orders_update(number):
    # create an SQLAlchemy query to get a reference of the order to be updated
    order = Order.query.filter_by(number=number).first()
    if order:
        order.status = request.form['status']
        db.session.commit()
        flash('Order status updated successfully!', 'success')
        return redirect(url_for('orders_admin'))
    else:
        flash('Order not found!', 'error')
        return redirect(url_for('orders_admin'))
    

@app.route('/orders/new', methods=['GET'])
@login_required
def new_order():
    # Check if there are existing items in the session
    if 'items' in session:
        # Redirect to the order creation page without clearing order_data
        return redirect(url_for('orders_create'))

    # Clear the session data only if there are no existing items
    session.pop('order_data', None)
    session.pop('items', None)

    
    # Redirect to the order creation page
    return redirect(url_for('orders_create'))
    
# create orders
@app.route('/orders/create', methods=['GET','POST'])
@login_required
def orders_create():
    form = CreateOrderForm()
    
    if 'order_data' in session:
        form.number.data = session['order_data']['number']
        form.status.data = session['order_data']['status']
        form.creation_date.data = datetime.strptime(session['order_data']['creation_date'], "%Y-%m-%d")
    
    products = Product.query.all()
    form.code.choices = [(product.code, product.code) for product in products]

    # If the add_item button was pressed
    if 'add_item' in request.form:
        item_data = {
            'product_code': form.code.data,
            'quantity': form.quantity.data,
            'width': form.width.data,
            'height': form.height.data
        }
        
        # Always update the order details in session
        session['order_data'] = {
            'number': form.number.data,
            'status': form.status.data,
            'creation_date': form.creation_date.data.strftime("%Y-%m-%d")
        }
        print("added data to sesh")

        # Add item data to session
        if 'items' not in session:
            session['items'] = []
        session['items'].append(item_data)
        session.modified = True  # Explicitly mark the session as modified

        return redirect(url_for('orders_create'))

    return render_template('orders_create.html', form=form, current_items=session.get('items', []))

# clear orders
@app.route('/orders/clear', methods=['GET','POST'])
@login_required
def clear_order():
    # Clear the session data
    session.pop('order_data', None)
    session.pop('items', None)
    return redirect(url_for('orders_create'))

# submit orders
@app.route('/orders/submit', methods=['POST'])
@login_required
def submit_order():
    form = CreateOrderForm()
    if not session.get('items'):
        flash('No items to submit!', 'error')
        return redirect(url_for('orders_create'))

    # If the main form was submitted
    if 'submit_order' in request.form:
        order_number = form.number.data

        # Ensure that the current_user is a Reseller
        if isinstance(current_user, Reseller):
            items_for_order = Item.query.filter_by(order_number=order_number).all()
            new_order = Order(
                user_email=current_user.email,
                number=session['order_data']['number'],
                status=session['order_data']['status'],
                creation_date=form.creation_date.data,
                items=items_for_order
            )
            current_user.orders.append(new_order)
            db.session.add(new_order)
            db.session.flush()  # Flush to get the order number for items (if auto-incremented)

            # Add items from session to the database
            for item_data in session.get('items', []):
                new_item = Item(
                    order_number=new_order.number,  # Link item to order
                    product_code=item_data['product_code'],
                    quantity=item_data['quantity'],
                    width=item_data['width'],
                    height=item_data['height']
                )
                db.session.add(new_item)

            db.session.commit()

            # Clear session data
            session.pop('order_data', None)
            session.pop('items', None)

            flash('Order created successfully!', 'success')
            return redirect(url_for('orders'))
        else:
            flash('Only resellers can create orders!', 'error')
            return redirect(url_for('orders_create'))

    return render_template('orders_create.html', form=form, current_items=session.get('items', []))

# read orders
@app.route('/orders/<number>', methods=['GET'])
@login_required
def orders_read(number):
    # create an SQLAlchemy query to get a reference of the order to be read
    order = Order.query.filter_by(number=number,user_email=current_user.email).first()
    # then pass that reference to the template
    return render_template('orders_read.html', order=order)

# read orders admin
@app.route('/orders/admin/<number>', methods=['GET','POST'])
def orders_read_admin(number):
    # create an SQLAlchemy query to get a reference of the order to be read
    order = Order.query.filter_by(number=number).first()
    # then pass that reference to the template
    return render_template('orders_read.html', order=order)

# go to URL http://localhost:5000/debug/orders to check what's currently in the orders table
@app.route('/debug/orders', methods=['GET'])
def debug_orders():
    all_orders = Order.query.all()  # Fetch all records from the "orders" table
    if all_orders == []:
        print("No orders found!")
    for order in all_orders:
        print("Order Number:", order.number)
        print("Creation Date:", order.creation_date)
        print("Status:", order.status)
        print("User Email:", order.user_email)
        print("-------------------")
    return "Check the console/log for the order details."

# delete orders
@app.route('/orders/<number>/delete', methods=['Get','POST'])
@login_required
def orders_delete(number):
    # admin delete
    if isinstance(current_user, Admin):
        order = Order.query.filter_by(number=number).first()
        db.session.delete(order)
        db.session.commit()
        
        session.pop('current_items', None)
        
        return redirect(url_for('orders_admin'))
    # create an SQLAlchemy query to get a reference of the order to be deleted
    order = Order.query.filter_by(number=number,user_email=current_user.email).first()
    # then call delete (passing that reference) followed by commit
    db.session.delete(order)
    db.session.commit()
    
    session.pop('current_items', None)
    
    return redirect(url_for('orders'))

# products
@app.route('/orders/admin/products', methods=['GET','POST'])
def products():
    products = Product.query.all()
    return render_template('products.html', products=products)

#create products
@app.route('/orders/admin/products/create', methods=['GET','POST'])
def products_create():
    form = ProductForm()
    if form.validate_on_submit():
        new_product = Product(
            code=form.code.data,
            description=form.description.data,
            price=form.price.data,
            available=form.available.data
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('products'))
    return render_template('products_create.html', form=form)

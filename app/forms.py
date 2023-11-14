'''
where forms will go. Todo:
[User forms] (all users)
sign up form (done)
sign in form (done)

[Reseller forms] (available to resellers, should admin have access too?)
create order

[Admin Form] (only appears if logged in user is an admin)
manage orders
add product
update product
'''
from flask import request
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, TextAreaField, DateField, SubmitField, validators, SelectField, BooleanField, FloatField, IntegerField
from wtforms.validators import DataRequired
from app.models import Product

class SignUpForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    passwd_confirm = PasswordField('Confirm Password', validators=[DataRequired(), validators.EqualTo('passwd', message='Passwords must match.')])
    company = StringField('Company', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    website = StringField('Website', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    passwd = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class CreateOrderForm(FlaskForm):
    code = SelectField('Product Code', validators=[DataRequired()])
    number = StringField('Order Number', validators=[DataRequired()])
    creation_date = DateField('Creation Date', validators=[DataRequired()], default=datetime.today)
    status = SelectField('Order Status', choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('complete', 'Complete')], validators=[DataRequired()], default='pending')
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    width = FloatField('Width', validators=[DataRequired()])
    height = FloatField('Height', validators=[DataRequired()])
    add_item = SubmitField('Add Item to Order')
    clear_order = SubmitField('Clear Order')
    submit_order = SubmitField('Submit Order')
    
class OrderForm(FlaskForm):
    status = SelectField('Order Status', choices=[('pending', 'Pending'), ('in progress', 'In Progress'), ('complete', 'Complete')], validators=[DataRequired()], default='pending')
    submit = SubmitField('Submit Order')

# Add & Update Product form
class ProductForm(FlaskForm):
    code = StringField('Product Code', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    available = BooleanField('Available')
    price = FloatField('Price', validators=[DataRequired()])
    submit = SubmitField('Submit Product')

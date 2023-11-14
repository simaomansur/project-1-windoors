from app_template import db 
from datetime import datetime
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    email = db.Column(db.String, primary_key=True)
    passwd = db.Column(db.String)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String)
    
    __mapper_args__ = {
        'polymorphic_identity':'user',
        'polymorphic_on':type
    }

class Admin(User):
    
    name = db.Column(db.String)
    title = db.Column(db.String)
    
    __mapper_args__ = {
        'polymorphic_identity':'admin'
    }

class Reseller(User):
    company = db.Column(db.String)
    address = db.Column(db.String)
    phone = db.Column(db.String)
    website = db.Column(db.String)
    
    __mapper_args__ = {
        'polymorphic_identity':'reseller'
    }

# * Product: code, description, type (window or door), available (true/false), price
class Product(db.Model):
    __tablename__ = 'products'
    code = db.Column(db.String, primary_key=True)
    description = db.Column(db.String)
    type = db.Column(db.String)
    available = db.Column(bool)
    price = db.Column(db.Integer)
    items = db.relationship('Item', back_populates='product')
    
class Order(db.Model):
    __tablename__ = 'orders'
    number = db.Column(db.Integer, primary_key=True)
    creation_date = db.Column(db.DateTime)
    status = db.Column(db.String)
    items = db.relationship('Item', back_populates='order')
    user_email = db.Column(db.String, db.ForeignKey('users.email')) # user who placed the order


class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.Integer, db.ForeignKey('orders.number'))
    sequential_number = db.Column(db.Integer) # Line nbr. will need to handle this in code
    product_code = db.Column(db.String, db.ForeignKey('products.code'))
    quantity = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    order = db.relationship('Order', back_populates='items')
    product = db.relationship('Product', back_populates='items')



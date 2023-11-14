from app import db, app
from app.models import Admin, Product
import bcrypt

def seed_database():
    with app.app_context():
        # Hash the password
        password = '1'.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password, salt)

        # Check if a user with the unhashed password exists
        existing_user = Admin.query.filter_by(email='tmota').first()
        existing_product1 = Product.query.filter_by(code='door-001').first()
        existing_product2 = Product.query.filter_by(code='door-002').first()
        existing_product3 = Product.query.filter_by(code='window-001').first()

        # If they exist, delete them
        if existing_user:
            db.session.delete(existing_user)
        if existing_product1:
            db.session.delete(existing_product1)
        if existing_product2:
            db.session.delete(existing_product2)
        if existing_product3:
            db.session.delete(existing_product3)
        db.session.commit()

        # Now, create and add the new records
        admin = Admin(email='tmota', passwd=hashed_password.decode('utf-8'))
        p1 = Product(code='door-001', description='Door 1', type='door', available=True, price=100.00, image='door-001.jpg')
        print(p1.code, p1.description, p1.type, p1.available, p1.price, p1.image)
        p2 = Product(code='door-002', description='Door 2', type='door', available=True, price=200.00, image='door-002.jpg')
        print(p2.code, p2.description, p2.type, p2.available, p2.price, p2.image)
        p3 = Product(code='window-001', description='Window 1', type='window', available=True, price=50.00, image='window-001.jpg')
        print(p3.code, p3.description, p3.type, p3.available, p3.price, p3.image)

        db.session.add(admin)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.commit()

            
if __name__ == '__main__':
    seed_database()
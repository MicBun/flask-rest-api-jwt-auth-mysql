import app

db = app.db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    city = db.Column(db.String(255))
    state = db.Column(db.String(255))
    postal = db.Column(db.Integer)
    password = db.Column(db.String(255), default="password")
    orders = db.relationship('Order', back_populates='user')

    def __init__(self, name, city, state, postal, password="password"):
        self.name = name
        self.city = city
        self.state = state
        self.postal = postal
        self.password = password

    def __repr__(self):
        return f"User(name={self.name}, city={self.city}, state={self.state}, postal={self.postal})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "postal": self.postal,
            "password": self.password
        }


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    category = db.Column(db.String(255))
    sub_category = db.Column(db.String(255))

    def __init__(self, name, category, sub_category):
        self.name = name
        self.category = category
        self.sub_category = sub_category

    def __repr__(self):
        return f"Product(name={self.name}, category={self.category}, sub_category={self.sub_category})"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "sub_category": self.sub_category
        }


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    quantity = db.Column(db.Integer)
    user = db.relationship('User', back_populates='orders')
    product = db.relationship('Product')

    def __init__(self, user_id, product_id, quantity):
        self.user_id = user_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return f"Order(user_id={self.user_id}, product_id={self.product_id}, quantity={self.quantity})"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity
        }

import datetime
import jwt
from datetime import timedelta
from flask import request, jsonify, redirect
from flask_jwt_extended import create_access_token, jwt_required
from app import db, app, database_space, user_space, product_space, order_space
from models import User, Product, Order
from flask_restx import Resource


@app.route('/swagger')
def swagger_ui():
    return redirect('/static/swagger.html')


def get_user_id_from_token():
    token = request.headers.get("Authorization")
    if token:
        token = token.split(" ")[1]
        print(token)
        try:
            payload = jwt.decode(token, app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
            print(payload)
            user_id = payload["sub"]["user_id"]
            return user_id
        except:
            return
    return


def is_admin():
    if get_user_id_from_token() == 0:
        return True
    return False


def reset_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    users_csv = open("users.csv", "r")
    products_csv = open("products.csv", "r")
    users_csv.readline()
    for line in users_csv:
        line = line.split(",")
        line[-1] = line[-1][:-1]
        user = User(line[1], line[2], line[3], line[4])
        db.session.add(user)
    db.session.commit()
    products_csv.readline()
    for line in products_csv:
        line = line.split(";")
        line[-1] = line[-1].replace("\n", "")
        product = Product(name=line[1], category=line[2], sub_category=line[3])
        db.session.add(product)
    db.session.commit()


@database_space.route("/reset-database")
class ResetDatabase(Resource):
    @database_space.header("Authorization", "JWT Token", required=True)
    @database_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def post(self):
        """Reset the database"""
        if not is_admin():
            return {"message": "Unauthorized"}, 401
        reset_db()
        return {"message": "Database reset"}, 200


@user_space.route("/users/all")
class Users(Resource):
    @user_space.header("Authorization", "JWT Token", required=True)
    @user_space.doc(
        summary="Get all users in the database (admin only)",
        description="This endpoint returns a list of all users in the database. It is restricted to admin users only.",
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def get(self):
        """Get all users in the database (admin only)"""
        if not is_admin():
            return {"message": "Unauthorized"}, 401
        users = User.query.all()
        return jsonify([e.to_dict() for e in users])


@user_space.route("/users/get/<int:user_id>")
class UserById(Resource):
    @user_space.header("Authorization" "JWT Token", required=True)
    @user_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def get_user_by_id(self, user_id):
        """Get a user by id (admin only)"""
        if not is_admin():
            return {"message": "Unauthorized"}, 401
        user = User.query.filter_by(id=user_id).first()
        if user:
            return jsonify(user.to_dict())


@user_space.route("/login")
class Login(Resource):
    @user_space.doc(
        summary="Login",
        description="This endpoint returns a JWT token to be used for authentication.",
        params={
            'body': {
                'in': 'body',
                'description':
                    'Input your id and password',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'id': {
                            'type': 'integer'
                        },
                        'password': {
                            'type': 'string'
                        }
                    },
                    'required': ['id', 'password']
                }}})
    def post(self):
        """Login to the system and get a JWT token (valid for 1 hour) to access the other endpoints"""
        data = request.get_json()
        if data["id"] == 0 and data["password"] == "admin":
            payload = {
                "user_id": 0,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            access_token = create_access_token(identity=payload, expires_delta=timedelta(days=1), fresh=True)
            return {"access_token": access_token}, 200
        user = User.query.filter_by(id=data["id"]).first()
        if user and user.password == data["password"]:
            payload = {
                "user_id": user.id,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
            }
            access_token = create_access_token(identity=payload, expires_delta=timedelta(days=1), fresh=True)
            access_token_str = access_token.decode('utf-8')
            return {"access_token": access_token_str}, 200


@user_space.route("/register")
class Register(Resource):
    @user_space.doc(
        summary="Register",
        description="This endpoint allows you to register a new user.",
        params={
            'body': {
                'in': 'body',
                'description':
                    'Input your name, city, state, postal code and password. The id will be automatically generated. '
                    'The id will be used to login. The password is optional and will be set to "password" if not '
                    'provided.',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'city': {
                            'type': 'string'
                        },
                        'state': {
                            'type': 'string'
                        },
                        'postal': {
                            'type': 'string'
                        },
                        'password': {
                            'type': 'string'
                        }
                    },
                    'required': ['name', 'city', 'state', 'postal']
                }}})
    def post(self):
        """Register a new user"""
        data = request.get_json()
        user = User.query.filter_by(name=data["name"]).first()
        if user:
            return {"message": "name taken"}, 400
        user = User(
            name=data["name"],
            city=data["city"],
            state=data["state"],
            postal=data["postal"],
            password=data["password"],
        )
        db.session.add(user)
        db.session.commit()
        return {"message": "success", "user": user.to_dict()}, 200


@user_space.route("/users/update")
class EditUser(Resource):
    @user_space.header("Authorization", "JWT Token", required=True)
    @user_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            },
            'body': {
                'in': 'body',
                'description':
                    'Input your name, city, state, postal and password. Only the fields you want to update are '
                    'required.',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'city': {
                            'type': 'string'
                        },
                        'state': {
                            'type': 'string'
                        },
                        'postal': {
                            'type': 'string'
                        },
                        'password': {
                            'type': 'string'
                        }
                    }}}})
    @jwt_required()
    def put(self):
        """Edit a user (user only)"""
        if is_admin():
            return {"message": "Only users can edit their own profile"}, 401
        data = request.get_json()
        user_id = get_user_id_from_token()
        user = User.query.filter_by(id=user_id).first()
        if user:
            if "name" in data:
                if User.query.filter_by(name=data["name"]).first():
                    return {"message": "name taken"}, 400
                user.name = data["name"]
            if "city" in data:
                user.city = data["city"]
            if "state" in data:
                user.state = data["state"]
            if "postal" in data:
                user.postal = data["postal"]
            if "password" in data:
                user.password = data["password"]
            db.session.commit()
            return {"message": "success"}, 200
        return {"message": "user not found"}, 404


@user_space.route("/users/delete/<int:user_id>")
class DeleteUser(Resource):
    @user_space.header("Authorization", "JWT Token", required=True)
    @user_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def delete(self, user_id):
        """Delete a user (admin only)"""
        if not is_admin():
            return {"message": "Unauthorized"}, 401
        user = User.query.filter_by(id=user_id).first()
        if user:
            db.session.delete(user)
            db.session.commit()
            return {"message": "success"}, 200
        return {"message": "user not found"}, 404


@product_space.route("/products/all")
class Products(Resource):
    def get(self):
        """Get all products in the database"""
        products = Product.query.all()
        return jsonify([e.to_dict() for e in products])


@product_space.route("/products/search/<string:query>")
class SearchProducts(Resource):
    def get(self, query):
        """Search for products by name"""
        if not query:
            return {"message": "query is required"}, 400
        products = Product.query
        if query:
            products = products.filter(
                Product.name.contains(query) | Product.category.contains(query) | Product.sub_category.contains(query))
            if products.count() == 0:
                return {"message": "no products found"}, 404
            return jsonify([e.to_dict() for e in products])
        return jsonify([e.to_dict() for e in products])


@product_space.route("/products/get/<int:id>")
class ProductById(Resource):
    def get(self, id):
        """Get a product by id"""
        product = Product.query.filter_by(id=id).first()
        return jsonify(product.to_dict())


@product_space.route("/products/add")
class AddProduct(Resource):
    @product_space.header("Authorization", "JWT Token", required=True)
    @product_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            },
            'body': {
                'in': 'body',
                'description':
                    'Input your product name, category, sub_category',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'category': {
                            'type': 'string'
                        },
                        'sub_category': {
                            'type': 'string'
                        }
                    },
                    'required': ['name', 'category', 'sub_category']
                }}})
    @jwt_required()
    def post(self):
        """Add a new product (admin only)"""
        if not is_admin():
            return {"message": "Not authorized"}, 401
        data = request.get_json()
        product = Product.query.filter_by(name=data["name"]).first()
        if product:
            return {"message": "product already exists"}, 400
        product = Product(
            name=data["name"],
            category=data["category"],
            sub_category=data["sub_category"],
        )
        db.session.add(product)
        db.session.commit()
        return {"message": "success", "product": product.to_dict()}, 200


@product_space.route("/products/edit/<int:id>")
class EditProduct(Resource):
    @product_space.header("Authorization", "JWT Token", required=True)
    @product_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            },
            'body': {
                'in': 'body',
                'description':
                    'Input your product name, category, sub_category. Only the fields you want to update are '
                    'required.',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {
                            'type': 'string'
                        },
                        'category': {
                            'type': 'string'
                        },
                        'sub_category': {
                            'type': 'string'
                        }
                    }}}})
    @jwt_required()
    def put(self, id):
        """Edit a product (admin only)"""
        if not is_admin():
            return jsonify({"message": "Not authorized"})
        product = Product.query.filter_by(id=id).first()
        if not product:
            return {"message": "product not found"}, 404
        data = request.get_json()
        if "name" in data:
            product.name = data["name"]
        if "category" in data:
            product.category = data["category"]
        if "sub_category" in data:
            product.sub_category = data["sub_category"]
        db.session.commit()
        return {"message": "success", "product": product.to_dict()}, 200


@product_space.route("/products/<int:id>")
class DeleteProduct(Resource):
    @product_space.header("Authorization", "JWT Token", required=True)
    @product_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def delete(self, id):
        """Delete a product (admin only)"""
        if not is_admin():
            return jsonify({"message": "Not authorized"})
        product = Product.query.filter_by(id=id).first()
        if not product:
            return {"message": "product not found"}, 404
        db.session.delete(product)
        db.session.commit()
        return {"message": "success"}, 200


@order_space.route("/orders/all")
class Orders(Resource):
    @order_space.header("Authorization", "JWT Token", required=True)
    @order_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def get(self):
        """Get all orders for a user or all orders if admin"""
        if is_admin():
            orders = Order.query.all()
            return jsonify([e.to_dict() for e in orders])
        user_id = get_user_id_from_token()
        orders = Order.query.filter_by(user_id=user_id).all()
        return jsonify([e.to_dict() for e in orders])


@order_space.route("/orders/get/<int:id>")
class OrderById(Resource):
    @order_space.header("Authorization", "JWT Token", required=True)
    @order_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def get(self, id):
        """Get order by id"""
        if is_admin():
            order = Order.query.filter_by(id=id).first()
            return jsonify(order.to_dict())
        user_id = get_user_id_from_token()
        order = Order.query.filter_by(id=id, user_id=user_id).first()
        if not order:
            return {"message": "order not found for user, or not authorized"}, 404
        return jsonify(order.to_dict())


@order_space.route("/orders/add")
class CreateOrder(Resource):
    @order_space.header("Authorization", "JWT Token", required=True)
    @order_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            },
            'body': {
                'in': 'body',
                'description':
                    'Input your product id, quantity',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'product_id': {
                            'type': 'integer'
                        },
                        'quantity': {
                            'type': 'integer'
                        }
                    },
                    'required': ['product_id', 'quantity']
                }}})
    @jwt_required()
    def post(self):
        """Create an order for a user"""
        data = request.get_json()
        user_id = get_user_id_from_token()
        order = Order(
            user_id=user_id,
            product_id=data["product_id"],
            quantity=data["quantity"],
        )
        db.session.add(order)
        db.session.commit()
        return {"message": "success", "order": order.to_dict()}, 200


@order_space.route("/orders/edit/<int:id>")
class EditOrder(Resource):
    @order_space.header("Authorization", "JWT Token", required=True)
    @order_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            },
            'body': {
                'in': 'body',
                'description':
                    'Input the new product id and quantity. Only the fields you want to update are',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'product_id': {
                            'type': 'integer'
                        },
                        'quantity': {
                            'type': 'integer'
                        }
                    }}}})
    @jwt_required()
    def put(self, id):
        """Update order by id for user or admin"""
        if is_admin():
            order = Order.query.filter_by(id=id).first()
            if not order:
                return {"message": "order not found"}, 404
            data = request.get_json()
            if "user_id" in data:
                order.user_id = data["user_id"]
            if "product_id" in data:
                order.product_id = data["product_id"]
            if "quantity" in data:
                order.quantity = data["quantity"]
            db.session.commit()
            return {"message": "success", "order": order.to_dict()}, 200
        user_id = get_user_id_from_token()
        order = Order.query.filter_by(id=id, user_id=user_id).first()
        if not order:
            return {"message": "order not found for user, or not authorized"}, 404
        data = request.get_json()
        if "product_id" in data:
            order.product_id = data["product_id"]
        if "quantity" in data:
            order.quantity = data["quantity"]
        db.session.commit()
        return {"message": "success", "order": order.to_dict()}, 200


@order_space.route("/orders/delete/<int:id>")
class DeleteOrder(Resource):
    @order_space.header("Authorization", "JWT Token", required=True)
    @order_space.doc(
        params={
            'Authorization': {
                'in': 'header',
                'description':
                    'Input your JWT token by adding "Bearer " then your token'
            }})
    @jwt_required()
    def delete(self, id):
        """Delete order by id for user or admin"""
        if is_admin():
            order = Order.query.filter_by(id=id).first()
            if not order:
                return {"message": "order not found"}, 404
            db.session.delete(order)
            db.session.commit()
            return {"message": "success"}, 200
        user_id = get_user_id_from_token()
        order = Order.query.filter_by(id=id, user_id=user_id).first()
        if not order:
            return {"message": "order not found for user, or not authorized"}, 404
        db.session.delete(order)
        db.session.commit()
        return {"message": "success"}, 200

from dotenv import dotenv_values
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
# from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy


env = dotenv_values(".env")


class Config:
    MYSQL_USERNAME = env["MYSQL_USERNAME"]
    MYSQL_PASSWORD = env["MYSQL_PASSWORD"]
    MYSQL_HOST = env["MYSQL_HOST"]
    MYSQL_PORT = env["MYSQL_PORT"]
    MYSQL_DB = env["MYSQL_DB"]


SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{Config.MYSQL_USERNAME}:{Config.MYSQL_PASSWORD}@" \
                          f"{Config.MYSQL_HOST}:{Config.MYSQL_PORT}/{Config.MYSQL_DB}"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URL
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
rest_app = Api(app=app)
product_space = rest_app.namespace('Product', description="CRUD Product")
order_space = rest_app.namespace('Order', description="CRUD Order")
database_space = rest_app.namespace('Database', description="Database")
user_space = rest_app.namespace('Users', description="CRUD User")
# rest_app.add_namespace(user_space)
# rest_app.add_namespace(product_space)
# rest_app.add_namespace(order_space)
# rest_app.add_namespace(database_space)
# rest_app.add_namespace(main_space)
db = SQLAlchemy(app)
jwt = JWTManager(app)
from router import *

if __name__ == '__main__':
    app.run()

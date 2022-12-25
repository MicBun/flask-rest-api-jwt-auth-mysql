from dotenv import dotenv_values
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restx import Api
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
description = (
    'A simple Flask REST API App with JWT Authentication and SQLAlchemy ORM '
    'integration with MySQL database backend and Swagger UI for API documentation and testing purposes. \n'
    'Author: @MicBun (Michael Buntarman)\n'
    'Github: https://github.com/MicBun \n'
    'LinkedIn: https://www.linkedin.com/in/micbun'
)
rest_app = Api(app=app, version='1.0',
               title='Flask REST API with Flask-RESTX, Flask-SQLAlchemy, JWT Auth, and MySQL',
               description=description)
product_space = rest_app.namespace('Product', description="CRUD Product")
order_space = rest_app.namespace('Order', description="CRUD Order")
database_space = rest_app.namespace('Database', description="Database")
user_space = rest_app.namespace('Users', description="CRUD User")
db = SQLAlchemy(app)
jwt = JWTManager(app)
from router import *

if __name__ == '__main__':
    app.run()

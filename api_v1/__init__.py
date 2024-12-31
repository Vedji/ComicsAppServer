from flask import Flask, g
from flask import Blueprint
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from mysql.connector.pooling import MySQLConnectionPool

app = Flask(__name__)
bp = Blueprint('main', __name__)

# Настройки подключения к базе данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://comicsappdb:0*9%/e0E1&m9f2@85.192.49.28/ComicsAppDB'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_SIZE'] = 10  # Размер пула соединений
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 120  # Таймаут соединений
app.config['SQLALCHEMY_POOL_RECYCLE'] = 100  # Рецикл соединений
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 5  # Допустимое превышение пула
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True
}

db = SQLAlchemy(app)


def create_app():

    app.config['JWT_SECRET_KEY'] = 'Tornado'
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    JWTManager(app)

    # imports db requests
    import api_v1.db_book
    import api_v1.db_file
    import api_v1.db_genres

    # Imports api
    import api_v1.api_book
    import api_v1.api_file
    import api_v1.api_genres

    # Imports html pages

    import api_v1.html_routes

    # Регистрируем маршруты (routes)
    app.register_blueprint(bp)

    return app
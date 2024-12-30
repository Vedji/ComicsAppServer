from flask import Flask
from flask import Blueprint
from datetime import datetime, timedelta
from flask_jwt_extended import JWTManager
import mysql.connector

bp = Blueprint('main', __name__)

# Конфигурация базы данных
conn = mysql.connector.connect(
        host="85.192.49.28",        # Адрес сервера MySQL (может быть IP-адрес или доменное имя)
        user="comicsappdb",         # Ваше имя пользователя MySQL
        password="0*9%/e0E1&m9f2",  # Ваш пароль от MySQL
        database="ComicsAppDB"      # Имя базы данных, к которой вы хотите подключиться
    )



def create_app():
    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = 'Tornado'
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    jwt = JWTManager(app)

    # imports db requests
    import api_v1.db_book
    import api_v1.db_file

    # Imports api
    import api_v1.api_book
    import api_v1.api_file

    # Регистрируем маршруты (routes)
    app.register_blueprint(bp)

    return app
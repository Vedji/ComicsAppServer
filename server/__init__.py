import logging
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from server.config import Config
Config.load_config()



app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = Config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = Config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_POOL_SIZE'] = Config.SQLALCHEMY_POOL_SIZE # Размер пула соединений
app.config['SQLALCHEMY_POOL_TIMEOUT'] = Config.SQLALCHEMY_POOL_TIMEOUT  # Таймаут соединений
app.config['SQLALCHEMY_POOL_RECYCLE'] = Config.SQLALCHEMY_POOL_RECYCLE  # Рецикл соединений
app.config['SQLALCHEMY_MAX_OVERFLOW'] = Config.SQLALCHEMY_MAX_OVERFLOW  # Допустимое превышение пула
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = Config.SQLALCHEMY_ENGINE_OPTIONS


app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = Config.JWT_REFRESH_TOKEN_EXPIRES


db = SQLAlchemy(app)


def create_app():
    JWTManager(app)
    from server.api.api_user import user_api
    from server.api.api_files import file_api
    from server.api.api_books import book_api
    from server.api.api_genre import genre_api
    from server.api.api_book_comments import book_comments_api
    from server.api.api_chapters import book_chapters_api
    from server.api.api_chapter_pages import book_chapter_pages_api
    from server.api.api_favorites import user_favorites_api

    app.register_blueprint(user_api, url_prefix='/api')
    app.register_blueprint(file_api, url_prefix='/api')
    app.register_blueprint(book_api, url_prefix='/api')
    app.register_blueprint(genre_api, url_prefix='/api')
    app.register_blueprint(book_comments_api, url_prefix='/api')
    app.register_blueprint(book_chapters_api, url_prefix='/api')
    app.register_blueprint(book_chapter_pages_api, url_prefix='/api')
    app.register_blueprint(user_favorites_api, url_prefix='/api')


    return app
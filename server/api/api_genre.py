import os.path
from re import search

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_

from server import Config
from server.api.extensions import ExtensionsReturned
from server.models.db_books import DBBooks
from server.models.db_files import DBFiles
from server.models.db_users import DBUser
from server.models.db_genre import DBGenre
from server.models.db_book_genres import DBBookGenre
from server import db

genre_api = Blueprint('genre_api', __name__)


@genre_api.route('/v1/genre/list', methods=['GET'])
def get_genre_list():
    genres = DBGenre.query.all()

    result = []
    for item in genres:
        result.append(
            {
                "genreID": item.genre_id,
                "genreName": item.name
            }
        )

    return {
        "genreList": result,
        "count": len(result)
    }




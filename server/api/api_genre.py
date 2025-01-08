import os.path
from re import search

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_

from server import Config
from server.api_response import ApiResponse
from server.api.extensions import ExtensionsReturned
from server.models.db_books import DBBooks
from server.models.db_files import DBFiles
from server.models.db_users import DBUser
from server.models.db_genre import DBGenre
from server.models.db_book_genres import DBBookGenre
from server import db
from server.exceptions import *
from server.api_response import ApiResponse

genre_api = Blueprint('genre_api', __name__)
register_error_handlers(genre_api)

@genre_api.route('/v1/genre/list', methods=['GET'])
def get_genre_list():
    genres = DBGenre.query.all()
    result = ApiResponse([ item.to_json() for item in genres ])
    return result.to_response()


@genre_api.route('/v2/books/<int:book_id>/getGenres', methods=['GET'])
def get_book_genres_v2(book_id: int):
    try:
        book = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        if book and book.genres:
            return ApiResponse([genre.to_json() for genre in book.genres]).to_response()
        else:
            return ApiResponse([]).to_response()
    except CustomException as error:
        return error.to_response()




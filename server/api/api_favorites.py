import logging
import pprint

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server.api.extensions import ExtensionsReturned
from server.exceptions import *
from server.models.db_books import DBBooks
from server.models.db_users import DBUser
from server.models.db_user_favorites import DBUserFavorites
from server import db

user_favorites_api = Blueprint('user_favorites_api', __name__)


@user_favorites_api.route('/v1/user/favorites', methods=['GET'])
@jwt_required()
def get_user_favorite_list():
    current_user_id = get_jwt_identity()
    arg_limit = request.args.get("limit", 10, int)
    arg_offset = request.args.get("offset", 0, int)

    if arg_limit < 0:
        return ExtensionsReturned.invalid_field("arg_limit", str(arg_limit))
    if arg_offset < 0:
        return ExtensionsReturned.invalid_field("arg_offset", str(arg_offset))

    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUserFavorites", current_user_id)

    user_favorites = user_who_added.favorites[arg_offset:arg_offset + arg_limit]
    result = []
    for item in user_favorites:
        result.append(item.to_json())
    return jsonify({
        "favoritesList": result,
        "count": len(result),
        "page": arg_offset // arg_limit if arg_limit > 0 else 0
    }), 200


@user_favorites_api.route('/v1/book/<int:book_id>/favorites', methods=['GET'])
@jwt_required()
def is_book_in_user_favorite_list(book_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUserFavorites", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)

    book_favorite = list(filter(lambda x: x.book_id == book_id, user_who_added.favorites))
    return jsonify({
        "isBookInUserFavoriteList": bool(book_favorite)
    }), 200


@user_favorites_api.route('/v1/book/<int:book_id>/favorites', methods=['POST'])
@jwt_required()
def add_book_in_user_favorite_list(book_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUserFavorites", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)

    book_favorite = list(filter(lambda x: x.book_id == book_id, user_who_added.favorites))
    if not book_favorite:
        try:
            new_favorite = DBUserFavorites(
                user_id = user_who_added.user_id,
                book_id = book_edit.book_id
            )
            db.session.add(new_favorite)
            db.session.commit()
        except Exception as e:
            logging.error(f"Ошибка при добавлении: {e}, в модели {book_favorite.__repr__()}.")
            db.session.rollback()
            return ExtensionsReturned.upload_error("ExtensionsReturned", book_favorite.__repr__())
    return jsonify({
        "isBookInUserFavoriteList": True
    }), 200


@user_favorites_api.route('/v1/book/<int:book_id>/favorites', methods=['PUT'])
@jwt_required()
def set_book_in_user_favorite_list(book_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUserFavorites", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)

    book_favorite = list(filter(lambda x: x.book_id == book_id, user_who_added.favorites))
    if book_favorite:
        try:
            is_book_in_favorite_list = False
            book_favorite = book_favorite[0]
            db.session.remove(book_favorite)
            db.session.commit()
        except Exception as e:
            logging.error(f"Ошибка при удалении: {e}, в модели {book_favorite.__repr__()}.")
            db.session.rollback()
            return ExtensionsReturned.upload_error("ExtensionsReturned", book_favorite.__repr__())
    else:
        try:
            new_favorite = DBUserFavorites(
                user_id = user_who_added.user_id,
                book_id = book_edit.book_id
            )
            is_book_in_favorite_list = True
            db.session.add(new_favorite)
            db.session.commit()
        except Exception as e:
            logging.error(f"Ошибка при добавлении: {e}, в модели {book_favorite.__repr__()}.")
            db.session.rollback()
            return ExtensionsReturned.upload_error("ExtensionsReturned", book_favorite.__repr__())
    return jsonify({
        "isBookInUserFavoriteList": is_book_in_favorite_list
    }), 200


@user_favorites_api.route('/v1/book/<int:book_id>/favorites', methods=['DELETE'])
@jwt_required()
def delete_book_in_user_favorite_list(book_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUserFavorites", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)

    book_favorite = list(filter(lambda x: x.book_id == book_id, user_who_added.favorites))

    if book_favorite:
        try:
            book_favorite = book_favorite[0]
            db.session.remove(book_favorite)
            db.session.commit()
        except Exception as e:
            logging.error(f"Ошибка при удалении: {e}, в модели {book_favorite.__repr__()}.")
            db.session.rollback()
            return ExtensionsReturned.upload_error("ExtensionsReturned", book_favorite.__repr__())
    return jsonify({
        "isBookInUserFavoriteList": False
    }), 200


# Api v2


@user_favorites_api.route('/v2/user/favorites', methods=['GET'])
@jwt_required()
def get_user_favorite_list_v2():
    try:
        current_user_id = get_jwt_identity()
        arg_limit = request.args.get("limit", 10, int)
        arg_offset = request.args.get("offset", 0, int)
        if arg_limit < 0:
            raise InvalidField("arg_limit", str(arg_limit),  "int", )
        if arg_offset < 0:
            raise InvalidField("arg_offset", str(arg_offset), "int", )
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        pprint.pprint(user_who_request.favorites)
        pprint.pprint([i.to_json_user_comments_list() for i in user_who_request.favorites])
        return ApiResponse([i.to_json_user_comments_list() for i in user_who_request.favorites]).to_response()
    except CustomException as error:
        return error.to_response()
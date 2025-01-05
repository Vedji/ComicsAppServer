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
from server.models.db_book_comments import DBBookComments
from server import db

book_comments_api = Blueprint('book_comments_api', __name__)


@book_comments_api.route('/v1/book_comments/<int:book_id>', methods=['GET'])
def get_book_comments_list(book_id: int):
    limit = request.args.get("limit", 10, int)
    offset = request.args.get("offset", 0, int)
    if not DBBooks.query.filter_by(book_id = book_id).first():
        return ExtensionsReturned.not_found('book_id', book_id)

    comment_query = DBBookComments.query

    comment_query = comment_query.filter_by(book_id = book_id)
    len_comments = comment_query.count()
    if limit > 0:
        comment_query = comment_query.limit(limit)
    if offset > 0:
        comment_query = comment_query.offset(offset)

    result = [item.to_json() for item in comment_query.all()]
    return jsonify(DBBookComments.list_to_json(
        result,
        offset // limit if limit > 0 else 0,
        len(result),
        len_comments
    )), 200


@book_comments_api.route('/v1/book_comments/<int:book_id>', methods=['POST'])
@jwt_required()
def add_book_comment(book_id: int):
    current_user_id = get_jwt_identity()
    user_who_requesting = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    if not user_who_requesting:
        return ExtensionsReturned.not_found("DBUser", current_user_id)

    args_rating = request.form.get("rating", -1, int)
    args_comment_text = request.form.get("comment", "", str)
    if args_rating < 0 or args_rating > 5:
        return ExtensionsReturned.invalid_field("rating", str(args_rating))

    comment = DBBookComments.query.filter(
        DBBookComments.user_id == user_who_requesting.user_id,
        DBBookComments.book_id == book_id
    ).first()
    if comment:
        return ExtensionsReturned.resource_has_exists(comment.__str__())

    comment = DBBookComments(
        book_id = book_id,
        user_id = user_who_requesting.user_id,
        rating = args_rating,
        comment = args_comment_text
    )
    if not comment.add_value():
        return ExtensionsReturned.upload_error("DBBookComments", comment.__str__())
    return jsonify(comment.to_json()), 201



@book_comments_api.route('/v1/book_comments/<int:book_id>', methods=['PUT'])
@jwt_required()
def edit_book_comment(book_id: int):
    current_user_id = int(get_jwt_identity())
    user_who_requesting = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    if not user_who_requesting:
        return ExtensionsReturned.not_found("DBUser", current_user_id)

    args_rating = request.form.get("rating", -1, int)
    args_comment_text = request.form.get("comment", "", str)
    print(book_id, current_user_id)
    comment = DBBookComments.query.filter(
        DBBookComments.user_id == user_who_requesting.user_id,
        DBBookComments.book_id == book_id
    ).first()
    print(comment)
    if not comment:
        return ExtensionsReturned.not_found('DBBookComments', comment.__str__())


    if 0 <= args_rating <= 5:
        comment.rating = args_rating
    comment.comment = args_comment_text

    if not comment.set_value():
        return ExtensionsReturned.upload_error("ExtensionsReturned", comment.__str__())

    return jsonify(comment.to_json()), 200


@book_comments_api.route('/v1/book_comments/<int:book_id>', methods=['DELETE'])
@jwt_required()
def delete_book_comment(book_id: int):
    current_user_id = int(get_jwt_identity())
    user_who_requesting = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    if not user_who_requesting:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    comment = DBBookComments.query.filter(
        DBBookComments.user_id == user_who_requesting.user_id,
        DBBookComments.book_id == book_id
    ).first()
    deleted_comment = comment.to_json()
    if not comment:
        return ExtensionsReturned.not_found('DBBookComments', comment.__str__())

    if not DBBookComments.remove_value(comment):
        return ExtensionsReturned.delete_error(str(comment))

    return jsonify(deleted_comment), 200
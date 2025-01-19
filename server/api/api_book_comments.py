import os.path
import pprint
from re import search

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_
from sqlalchemy.testing.suite.test_reflection import metadata

from server import Config
from server.api.extensions import ExtensionsReturned
from server.exceptions import *
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


@book_comments_api.route('/v2/book_comments/<int:book_id>', methods=['GET'])
def get_book_comments_list_v2(book_id: int):
    try:
        limit = request.args.get("limit", 10, int)
        offset = request.args.get("offset", 0, int)
        book = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        if book and book.comments:
            comments = book.comments
            result = []
            for comment in comments:
                result.append(comment.to_json_v2())
            total_count = len(result)
            return ApiResponse(
                result[offset:offset+limit],
                metadata = ApiResponse.pagination(limit, offset, total_count)
            ).to_response()
        else:
            return ApiResponse([], metadata = ApiResponse.pagination(limit, offset, 0)).to_response()
    except CustomException as error:
        return error.to_response()


@book_comments_api.route('/v2/book_comments/<int:book_id>/user_comment', methods=['GET'])
@jwt_required()
def get_user_comment_for_book_v2(book_id: int):
    try:
        current_user_id = int(get_jwt_identity())
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        book = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        user_comment = list(filter(lambda x: x.user_id == user_who_request.user_id, book.comments))
        if not user_comment:
            return ApiResponse({
                "aboutUser": {
                    "userID": user_who_request.user_id,
                    "userTitleImage": user_who_request.user_title_image,
                    "username": user_who_request.username
                },
                "bookId": book_id,
                "comment": "",
                "commentId": -1,
                "rating": 0,
                "uploadDate": ""
            }).to_response()
        return ApiResponse(user_comment[-1].to_json_v2()).to_response()
    except CustomException as error:
        return error.to_response()


@book_comments_api.route('/v2/book_comments/<int:book_id>/user_comment', methods=['PUT'])
@jwt_required()
def set_user_comment_for_book_v2(book_id: int):
    try:
        # Get comment body
        rating = request.form.get("rating", -1, int)
        comment_body = request.form.get("comment", "", str)
        if rating <= 0 or rating > 5:
            raise InvalidField("rating", rating, "Int[0:5]")
        if len(comment_body) < 10:
            raise InvalidField("comment", comment_body, "Str[len >= 10]")
        # Get user info
        current_user_id = int(get_jwt_identity())
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        book: DBBooks = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        user_comments: list[DBBookComments] = list(filter(lambda x: x.user_id == user_who_request.user_id, book.comments))
        if not user_comments:
            new_comment: DBBookComments = DBBookComments(
                user_id = user_who_request.user_id,
                book_id = book.book_id,
                rating = rating,
                comment = comment_body
            )
            db.session.add(new_comment)
            db.session.commit()
            return ApiResponse(new_comment.to_json_v2()).to_response()
        user_comment: DBBookComments = user_comments[-1]
        user_comment.comment = comment_body
        user_comment.rating = rating
        db.session.commit()
        return ApiResponse(user_comment.to_json_v2()).to_response()
    except CustomException as error:
        db.session.rollback()
        return error.to_response()
    except Exception as err:
        db.session.rollback()
        return CustomException(
            message=err.__repr__(),
            error=err.__class__
        ).to_response()


@book_comments_api.route('/v2/user/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_user_comment_for_book_v2(comment_id: int):
    try:
        # Get user info
        current_user_id = int(get_jwt_identity())
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        comment: DBBookComments = DBBookComments.query.filter(DBBookComments.comment_id == comment_id).first()
        pprint.pprint(comment)
        if not comment:
            raise NotFound("DBBookComments", comment_id, "Comment for delete not found")

        comment_deleted = comment.to_json_v2()
        comment_deleted["commentId"] = -1
        db.session.delete(comment)
        db.session.commit()
        return ApiResponse(comment_deleted).to_response()
    except CustomException as error:
        db.session.rollback()
        return error.to_response()
    except Exception as err:
        db.session.rollback()
        return CustomException(
            message=err.__repr__(),
            error=err.__class__
        ).to_response()
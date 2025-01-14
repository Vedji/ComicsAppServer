import pprint

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy import or_

from server.api.extensions import ExtensionsReturned
from server.models.db_book_comments import DBBookComments
from server.models.db_books import DBBooks
from server.models.db_users import DBUser
from server.exceptions import *
from server import db


user_api = Blueprint('user_api', __name__)
register_error_handlers(user_api)


@user_api.route('/v1/user/login', methods=['POST'])
def user_login():
    username = request.form.get('username', "", str)
    email = request.form.get('email', "", str)
    password_hash = request.form.get('password')

    print(username, email, password_hash)

    if not username and not email:
        raise InvalidField("username and email", None, "str")
    if not password_hash:
        raise InvalidField("password_hash", password_hash, "str")

    user_query = DBUser.query
    if not username and email:
        user_query = user_query.filter(DBUser.email == email, DBUser.password_hash == password_hash)
    elif username and not email:
        user_query = user_query.filter(DBUser.username == username, DBUser.password_hash == password_hash)
    elif username and email:
        user_query = user_query.filter(or_(DBUser.username == username, DBUser.email == email), DBUser.password_hash == password_hash)
    user = user_query.first()
    if not user:
        raise AuthorizationError(f"<User(username = {username}, email = {email})>")

    access_token = create_access_token(identity=str(user.user_id))
    refresh_token = create_refresh_token(identity=str(user.user_id))

    return jsonify({
        "aboutUser": user.to_json(),
        "accessToken": access_token,
        "refreshToken": refresh_token
    })


@user_api.route('/v1/user/<int:user_id>/info', methods=['GET'])
def user_info(user_id: int):
    if user_id < 0:
        raise  InvalidField("userID", user_id, "Int > 0")
    user = DBUser.query.filter(DBUser.user_id == user_id).first()
    if not user:
        raise NotFound(f"<User(user_id = {user_id})>")
    return jsonify(user.to_json()), 200


@user_api.route('/v1/user/comment/<int:book_id>', methods=['GET'])
@jwt_required()
def get_user_comment_for_book(book_id: int):
    current_user_id = int(get_jwt_identity())
    user_who_request = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_request:
        raise NotFound(f"<User(user_id = {current_user_id})>")
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    comment = list(filter(lambda x: x.user_id == user_who_request.user_id, book_edit.comments))
    if not comment:
        raise NotFound(f"<Comment(user_id = {current_user_id})>")
    if book_edit.book_added_by != user_who_request.user_id:
        raise NotPermission("User has not permision to this book")
    return jsonify(comment[0].to_json()), 200


@user_api.route('/v1/user/book/<int:book_id>/comment', methods=['POST'])
@jwt_required()
def add_user_comment_for_book(book_id: int):
    new_rating = request.form.get("rating", -1, int)
    new_comment = request.form.get("comment", "", str)
    current_user_id = int(get_jwt_identity())

    user_who_request = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()

    if not user_who_request:
        raise NotFound(f"<User(user_id = {current_user_id})>")
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    comment = list(filter(lambda x: x.user_id == user_who_request.user_id, book_edit.comments))
    if comment:
        raise ResourceHasExists(f"<Comment(user_id = {user_who_request.user_id}, book_id = {book_id})>")
    if not 0 < new_rating <= 5:
        raise InvalidField("rating", new_rating, "[0 < Int <= 5]")
    try:
        new_db_comment = DBBookComments(
            user_id=user_who_request.user_id,
            book_id=book_id,
            rating=new_rating,
            comment=new_comment
        )
        db.session.add(new_db_comment)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        raise UpdateError(
            "Comment",
            err.__str__(),
            500,
            user_id = current_user_id,
            book_id = book_id
        )
    return jsonify(new_db_comment.to_json()), 200


@user_api.route('/v1/user/book/<int:book_id>/comment/<int:comment_id>', methods=['PUT'])
@jwt_required()
def edit_user_comment_for_book(book_id: int, comment_id: int):
    new_rating = request.form.get("rating", -1, int)
    new_comment = request.form.get("comment", "", str)

    current_user_id = int(get_jwt_identity())
    user_who_request = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_request:
        raise NotFound(f"<User(user_id = {current_user_id})>")
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    comment = list(filter(lambda x: x.comment_id == comment_id, book_edit.comments))
    if not comment:
        raise NotFound(f"<Comment(user_id = {current_user_id})>")
    comment = comment[0]
    if book_edit.book_added_by != user_who_request.user_id:
        raise NotPermission("User has not permision to this book")
    if new_rating < 0:
        new_rating = comment.rating
    if not 0 < new_rating <= 5:
        raise InvalidField("rating", new_rating, "[0 < Int <= 5]")

    try:
        if comment.rating != new_rating and new_rating > 0:
            comment.rating = new_rating
        if comment.comment != new_comment:
            comment.comment = new_comment
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        raise UpdateError(
            "Comment",
            err.__repr__(),
            500,
            user_id = current_user_id,
            book_id = book_id,
            comment_id = comment_id
        )
    return jsonify(comment.to_json()), 200


@user_api.route('/v1/user/book/<int:book_id>/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_user_comment_for_book(book_id: int, comment_id: int):

    current_user_id = int(get_jwt_identity())
    user_who_request = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()

    if not user_who_request:
        raise NotFound(f"<User(user_id = {current_user_id})>")
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    comment = list(filter(lambda x: x.comment_id == comment_id, book_edit.comments))
    if not comment:
        raise NotFound(f"<Comment(user_id = {current_user_id})>")
    comment = comment[0]
    comment_deleted = comment.to_json()
    if book_edit.book_added_by != user_who_request.user_id and user_who_request.permission != 4:
        raise NotPermission("User has not permision to this book")
    try:
        db.session.delete(comment)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        raise DeleteError(
            "Comment",
            err.__repr__(),
            500,
            user_id = current_user_id,
            book_id = book_id,
            comment_id = comment_id
        )
    return jsonify(comment_deleted), 200



# Api v2 endpoints

@user_api.route('/v2/user/login', methods=['POST'])
def user_login_v2():
    try:
        username = request.form.get('username', "", str)
        email = request.form.get('email', "", str)
        password_hash = request.form.get('password')

        if not username and not email:
            raise InvalidField("username and email", None, "str")
        if not password_hash:
            raise InvalidField("password_hash", password_hash, "str")

        user_query = DBUser.query
        if not username and email:
            user_query = user_query.filter(DBUser.email == email, DBUser.password_hash == password_hash)
        elif username and not email:
            user_query = user_query.filter(DBUser.username == username, DBUser.password_hash == password_hash)
        elif username and email:
            user_query = user_query.filter(or_(DBUser.username == username, DBUser.email == email),
                                           DBUser.password_hash == password_hash)
        user = user_query.first()
        if not user:
            raise AuthorizationError(f"<User(username = {username}, email = {email})>")

        access_token = create_access_token(identity=str(user.user_id))
        refresh_token = create_refresh_token(identity=str(user.user_id))
        data = {
            "aboutUser": user.to_json(),
            "tokens": {
                "accessToken": access_token,
                "refreshToken": refresh_token,
                "bcryptToken": "None"
            }
        }
        return ApiResponse(data).to_response()
    except CustomException as error:
        return error.to_response()


@user_api.route('/v1/user/comments', methods=['GET'])
@jwt_required()
def get_user_comments_v2():
    try:
        current_user_id = int(get_jwt_identity())
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        pprint.pprint(user_who_request.comments)
        comments = [comment.to_json_for_one_user() for comment in user_who_request.comments]
        return ApiResponse(comments).to_response()
    except CustomException as error:
        return error.to_response()
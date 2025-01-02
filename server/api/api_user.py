from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token

from server.api.extensions import ExtensionsReturned
from server.models.db_users import DBUser


user_api = Blueprint('user_api', __name__)


@user_api.route('/v1/user/login', methods=['POST'])
def user_login():
    username = request.form.get('username')
    password_hash = request.form.get('password')
    if not username:
        return ExtensionsReturned.invalid_field("username", username)
    if not password_hash:
        return ExtensionsReturned.invalid_field("password_hash", password_hash)

    users = DBUser.query.filter(DBUser.username == username, DBUser.password_hash == password_hash).first()
    if not users:
        return ExtensionsReturned.not_found("User", username)

    access_token = create_access_token(identity=str(users.user_id))
    refresh_token = create_refresh_token(identity=str(users.user_id))

    return jsonify({
        "accessToken": access_token,
        "refreshToken": refresh_token
    })


@user_api.route('/v1/user/<int:user_id>/info', methods=['GET'])
def user_info(user_id: int):
    if user_id < 0:
        return ExtensionsReturned.invalid_field("user_id", str(user_id))
    user = DBUser.query.filter(DBUser.user_id == user_id).first()
    if not user:
        return ExtensionsReturned.not_found("User", user_id)
    return jsonify(user.to_json()), 200

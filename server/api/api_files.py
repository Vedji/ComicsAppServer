import os.path

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from server import Config, db
from server.api.extensions import *     # Lattest
from server.exceptions import *
from server.api_response import ApiResponse
from server.models.db_files import DBFiles
from server.models.db_users import DBUser

file_api = Blueprint('file_api', __name__)


@file_api.route('/v1/file/<int:file_id>/info', methods=['GET'])
def get_file_info(file_id: int):
    if file_id < 0:
        return ExtensionsReturned.invalid_field("file_id", "-1")
    file_info = DBFiles.query.filter(DBFiles.file_id == file_id).first()
    if not file_info:
        return ExtensionsReturned.not_found("File", file_id)
    return jsonify(file_info.to_json()), 200

@file_api.route('/v1/file/<int:file_id>/get', methods=['GET'])
def get_file(file_id: int):
    file_path = Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY
    if file_id < 0:
        return send_file(
            Config.linux_path(file_path + "\\_default\\file_not_found.jpg"),
            download_name='file_not_found.jpg',
            mimetype='image/jpeg'
        )
    file_info = DBFiles.query.filter(DBFiles.file_id == file_id).first()
    if not file_info:
        return send_file(
            Config.linux_path(file_path + "\\_default\\file_not_found.jpg"),
            download_name='file_not_found.jpg',
            mimetype='image/jpeg'
        )
    return send_file(
        Config.linux_path(file_path + "\\" + file_info.file_path + file_info.file_name),
        download_name=file_info.file_name,
        mimetype=file_info.file_type
    )


@file_api.route('/v2/files', methods=['PUT'])
@jwt_required()
def update_file_v2():
    try:
        current_user_id = get_jwt_identity()
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        if user_who_request.permission < 0:
            raise NotPermission("upload file")
        uploaded_file = request.files["uploadedFile"]
        mime_type = request.form.get("mimeType")
        server_file_path = "storage_v2/"
        if uploaded_file:
            db_file = DBFiles(
                added_by = user_who_request.user_id,
                file_path = server_file_path,
                file_name = "No saving_file",
                file_type = mime_type,
            )
            db.session.add(db_file)
            db.session.commit()
            file_name = f"file_{db_file.file_id}." + mime_type.split("/")[-1]
            uploaded_file.save(
                Config.linux_path(
                    Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY +"/" + server_file_path + file_name))
            db_file.file_name = file_name
            db.session.add(db_file)
            db.session.commit()
            return ApiResponse(db_file.to_json()).to_response()
        else:
            raise NotFound("DBFile", "uploadedFile")
    except CustomException as error:
        db.session.rollback()
        return error.to_response()
    except Exception as err:
        db.session.rollback()
        return CustomException(
            message=err.__repr__(),
            error=err.__class__
        ).to_response()


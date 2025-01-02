import os.path

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token

from server import Config
from server.api.extensions import ExtensionsReturned
from server.models.db_files import DBFiles

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
            file_path + "\\_default\\file_not_found.jpg",
            download_name='file_not_found.jpg',
            mimetype='image/jpeg'
        )
    file_info = DBFiles.query.filter(DBFiles.file_id == file_id).first()
    if not file_info:
        return send_file(
            file_path + "\\_default\\file_not_found.jpg",
            download_name='file_not_found.jpg',
            mimetype='image/jpeg'
        )
    return send_file(
        file_path + "\\" + file_info.file_path + file_info.file_name,
        download_name=file_info.file_name,
        mimetype=file_info.file_type
    )



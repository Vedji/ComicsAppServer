import os.path

from flask import request, send_file
import api_v1.db_file
from api_v1 import bp
from api_v1.db_data_returns import Files
from api_v1.errors import FileErrors
from api_v1.model_file import FileModel
import mimetypes
from api_v1 import db


@bp.route('/api/v1/file/get', methods=["GET"])
def get_file():
    file_id = request.args.get('file_id', 0, int)
    file = api_v1.db_file.get_file_info(file_id)
    if file and os.path.isfile(file["fileDirectory"]):
        return send_file(file["fileDirectory"], download_name=file["fileName"])
    return send_file(
        Files.DEFAULT_PATH + Files.DEFAULT_FILE_PATH + Files.DEFAULT_FILE_NAME,
        download_name=Files.DEFAULT_FILE_NAME
    )

@bp.route('/api/v1/file/info', methods=["GET"])
def get_file_info():
    file_id = request.args.get('file_id', -1, int)
    file = api_v1.db_file.get_file_info(file_id)
    return file if file else FileErrors.file_not_found(file_id)

@bp.route('/api/v1/file/upload', methods=["POST"])
def api_upload_file_info():
    """
    :param added_by: user id who add file
    :param file_path: example: 'dir1/'
    :param file_name: example: 'image.jpg'
    :return:
    """
    data = request.get_json()
    added_by: int = data.get('addedBy')
    file_path: str = data.get('filePath')
    file_name: str = data.get('fileName')
    if 'file' not in request.files:
        return FileErrors.file_not_uploaded()
    file = request.files['file']
    if file.filename == '':
        return FileErrors.file_not_selected()
    try:
        save_path = Files.DEFAULT_PATH + file_path + file_name
        file.save(save_path)
        file_type = mimetypes.guess_file_type(save_path)

        new_file = FileModel(
            added_by = added_by,
            file_name = file_name,
            file_type = file_type,
            file_path = file_path
        )
        db.session.add(new_file)
        db.session.commit()
        return Files.get_file_info(
            new_file.file_id,
            new_file.added_by,
            new_file.file_name,
            new_file.file_type,
            new_file.upload_date,
            new_file.file_path
        )
    except Exception as e:
        db.session.rollback()
        return FileErrors.other_errors_with_file(e)

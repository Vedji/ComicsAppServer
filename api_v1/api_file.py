from dbm import error

from flask import jsonify, request, send_file
import io
import api_v1.db_file
from api_v1 import conn
from api_v1 import bp
from api_v1.errors import FileErrors

@bp.route('/api/v1/file/get', methods=["GET"])
def get_file():
    file_id = request.args.get('file_id', 0, int)
    file = api_v1.db_file.get_file(conn, file_id)
    if file:
        file_stream = io.BytesIO(file['file_content'])
        file_stream.seek(0)
        return send_file(file_stream, download_name=file["file_name"])
    return FileErrors.file_not_found(file_id)

@bp.route('/api/v1/file/info', methods=["GET"])
def get_file_info():
    file_id = request.args.get('file_id', -1, int)
    file = api_v1.db_file.get_file_info(conn, file_id)
    return file if file else FileErrors.file_not_found(file_id)

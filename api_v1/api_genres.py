import os.path

from flask import request, send_file, jsonify
import api_v1.db_genres
from api_v1 import bp
from api_v1.db_data_returns import Files
from api_v1.errors import FileErrors

@bp.route('/api/v1/genre/list', methods=["GET"])
def get_api_genre():
    data = api_v1.db_genres.db_get_all_genres()
    return jsonify(data)
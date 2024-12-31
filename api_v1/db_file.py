import os
from api_v1.db_data_returns import Files
from api_v1.model_file import FileModel


def get_file_info(file_id: int):
    data = FileModel.query.filter_by(file_id=file_id).first()
    if data:
        return Files.get_file_info(
            data.file_id,
            data.added_by,
            data.file_name,
            data.file_type,
            data.upload_date.strftime("%H:%M:%S %d-%m-%Y"),
            data.file_path
        )
    return None

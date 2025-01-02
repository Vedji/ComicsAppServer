import os.path

from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP
from datetime import datetime


class DBFiles(db.Model):
    __tablename__ = 'files'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    added_by = db.Column(db.Integer, nullable=False, index=True)
    file_path = db.Column(db.String(4096), nullable=True, default='_default/file_not_found.jpg')
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    upload_date = db.Column(db.TIMESTAMP, nullable=True, default=datetime.utcnow, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f"<File {self.file_name} (ID: {self.file_id})>"

    def to_json(self):
        return {
            "fileID": self.file_id,
            "addedBy": self.added_by,
            "filePath": self.file_path,
            "fileName": self.file_name,
            "fileType": self.file_type,
            "uploadDate": self.upload_date.strftime(Config.DATE_FORMAT)

        }

    def add_file(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            db.session.rollback()
            return False
        return True
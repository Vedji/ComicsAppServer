from api_v1 import db


class FileModel(db.Model):
    __tablename__ = 'files'

    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    added_by = db.Column(db.Integer, nullable=False, index=True)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    upload_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)
    file_path = db.Column(db.String(4096), nullable=True, default='_default/file_not_found.jpg')

    def __repr__(self):
        return f"<File(file_id={self.file_id}, file_name='{self.file_name}', added_by={self.added_by})>"
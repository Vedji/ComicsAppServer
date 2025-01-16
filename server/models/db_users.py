from sqlalchemy.orm import relationship

from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP


class DBUser(db.Model):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    user_title_image = Column(Integer, ForeignKey('files.file_id'), nullable=False, default=2)  # Assuming 'images' table exists
    user_description = Column(Text, nullable=True)
    email = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    permission = db.Column(db.Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=True)

    comments = relationship('DBBookComments', back_populates='user')
    favorites = relationship('DBUserFavorites',back_populates='user')

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username='{self.username}', email='{self.email}')>"

    def to_json(self):
        return {
            "userID": self.user_id,
            "username": self.username,
            "userTitleImage": self.user_title_image,
            "userDescription": self.user_description,
            "email": self.email,
            "permission": self.permission,
            "createdAt": self.created_at.strftime(Config.DATE_FORMAT)
        }

    def to_json_briefly(self):
        return {
            "userID": self.user_id,
            "username": self.username,
            "userTitleImage": self.user_title_image,
            "userDescription": self.user_description
        }

    def to_json_for_comments(self):
        return {
            "userID": self.user_id,
            "username": self.username,
            "userTitleImage": self.user_title_image
        }
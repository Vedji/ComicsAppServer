from sqlalchemy.orm import relationship
from server import db
from server import Config
from server.models.db_model import DBModel
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP, DateTime
import logging


class DBBookComments(DBModel, db.Model):
    __tablename__ = 'book_comments'

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=True)

    # Relationships
    user = relationship('DBUser', back_populates='comments')
    book = relationship('DBBooks', back_populates='comments')

    def to_json(self):
        return {
            "commentID": self.comment_id,
            "userID": self.user_id,
            "bookID": self.book_id,
            "rating": self.rating,
            "comment": self.comment,
            "uploadDate": self.created_at.strftime(Config.DATE_FORMAT)
        }


    @staticmethod
    def to_list_json(comments_list: list, count: int, page: int, **kwargs):
        return {
            "commentsList": comments_list,
            "page": page,
            "count": count
        }

    def __repr__(self):
        return f"<BookComment(comment_id={self.comment_id}, user_id={self.user_id}, book_id={self.book_id}, rating={self.rating})>"
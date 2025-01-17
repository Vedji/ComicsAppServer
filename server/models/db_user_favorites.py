import pprint

from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from server import db, Config



class DBUserFavorites(db.Model):
    __tablename__ = 'user_favorites'

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    chapter_id = Column(Integer, ForeignKey('book_chapters.chapter_id'), default=-1)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)

    user = relationship('DBUser', back_populates='favorites')
    book = relationship('DBBooks', back_populates='favorite_by')
    chapter = relationship('DBBookChapters', back_populates='favorites')

    def to_json(self) -> dict:
        return {
            "favoriteId": self.favorite_id,
            "userId": self.user_id,
            "bookId": self.book_id,
            "chapterId": -1 if not self.chapter or not self.chapter_id else self.chapter.chapter_id,
            "uploadAt": self.created_at.strftime(Config.DATE_FORMAT)
        }

    @staticmethod
    def default(user_id, book_id):
        return {
            "favoriteId": -1,
            "userID": user_id,
            "bookId": book_id,
            "chapterId": -1,
            "uploadAt": ""
        }

    def to_json_user_comments_list(self):
        return {
            "favoriteId": self.favorite_id,
            # "bookID": self.book_id,
            "uploadAt": self.created_at.strftime(Config.DATE_FORMAT),
            # "aboutUser": -1 if not self.user else self.user.to_json_briefly(),
            "chapterId": -1 if not self.chapter or not self.chapter_id else self.chapter.chapter_id,
            "aboutBook":  -1 if not self.book else self.book.to_json(),
        }

    def __repr__(self):
        return f"<UserFavorites(favorite_id={self.favorite_id}, user_id={self.user_id}, book_id={self.book_id}, created_at={self.created_at})>"

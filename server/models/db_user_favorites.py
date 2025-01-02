from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from server import db, Config



class DBUserFavorites(db.Model):
    __tablename__ = 'user_favorites'

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)

    user = relationship('DBUser', back_populates='favorites')
    book = relationship('DBBooks', back_populates='favorite_by')

    def to_json(self) -> dict:
        return {
            "favoriteId": self.favorite_id,
            "userID": self.user_id,
            "bookID": self.book_id,
            "uploadAt": self.created_at.strftime(Config.DATE_FORMAT)
        }

    def __repr__(self):
        return f"<UserFavorites(favorite_id={self.favorite_id}, user_id={self.user_id}, book_id={self.book_id}, created_at={self.created_at})>"

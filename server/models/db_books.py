from email.policy import default

from sqlalchemy.orm import relationship

from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP, DECIMAL
from datetime import datetime


class DBBooks(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_added_by = db.Column(db.Integer, nullable=False, index=True)
    book_title = db.Column(db.String(255), nullable=False)
    book_title_image = db.Column(db.Integer, nullable=True, index=True, default=4)
    book_rating = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    book_date_publication = db.Column(db.String(16), nullable=True)
    book_description = db.Column(db.Text, nullable=True)
    book_isbn = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.TIMESTAMP, nullable=True, default=datetime.utcnow, server_default=db.func.current_timestamp())

    chapters = relationship('DBBookChapters', back_populates='book')
    genres = relationship('DBGenre', secondary='book_genres', back_populates='books')
    comments = relationship('DBBookComments', back_populates='book')
    favorite_by = relationship('DBUserFavorites',back_populates='book')


    def __repr__(self):
        return f"<Book {self.book_title} (ID: {self.book_id})>"

    def to_json(self):
        return {
            "bookID": self.book_id,
            "bookAddedBy": self.book_added_by,
            "bookTitle": self.book_title,
            "bookTitleImage": self.book_title_image,
            "bookRating": self.book_rating,
            "bookDatePublication": self.book_date_publication,
            "bookDescription": self.book_description,
            "bookISBN": self.book_isbn,
            "uploadDate": self.created_at.strftime(Config.DATE_FORMAT)
        }

    def add_book(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            db.session.rollback()
            return False
        return True

    @staticmethod
    def list_to_json(catalog_list: list, page: int, per_page: int, total: int):
        return {
            "pageItems": catalog_list,
            "totalCount": total,
            "page": page,
            "perPage": per_page
        }
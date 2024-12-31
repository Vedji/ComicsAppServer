from api_v1 import db
# Инициализация SQLAlchemy
# db = SQLAlchemy(app)

class BookGenreModel(db.Model):
    __tablename__ = 'book_genres'

    book_id = db.Column(db.Integer, primary_key=True, nullable=False)
    genre_id = db.Column(db.Integer, primary_key=True, nullable=False)

    def __repr__(self):
        return f"<BookGenre(book_id={self.book_id}, genre_id={self.genre_id})>"
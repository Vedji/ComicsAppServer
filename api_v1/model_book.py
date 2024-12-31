from api_v1 import db


# Инициализация SQLAlchemy
# db = SQLAlchemy(app)

class BookModel(db.Model):
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_added_by = db.Column(db.Integer, nullable=False, index=True)
    book_title = db.Column(db.String(255), nullable=False)
    book_title_image = db.Column(db.Integer, nullable=False, index=True)
    book_author = db.Column(db.String(100), nullable=True)
    book_date_of_publication = db.Column(db.String(16), nullable=True)
    book_rating = db.Column(db.Integer, nullable=True, default=0)
    book_description = db.Column(db.Text, nullable=True)
    book_isbn = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=True)

    def __repr__(self):
        return f"<Book(book_id={self.book_id}, book_title='{self.book_title}', book_author='{self.book_author}')>"
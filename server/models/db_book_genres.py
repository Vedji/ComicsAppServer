from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP


class DBBookGenre(db.Model):
    __tablename__ = 'book_genres'

    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'), primary_key=True, nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.genre_id'), primary_key=True, nullable=False)


    def to_json(self):
        return {
            "bookID": self.book_id,
            "genreID": self.genre_id
        }

    def __repr__(self):
        return f"<BookGenre BookID: {self.book_id}, GenreID: {self.genre_id}>"

    def add_row(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            print(f"Ошибка при добавлении записи: {e}")
            db.session.rollback()
            return False
        return True

    def delete_book_genre(self):
        try:
            # Поиск записи
            record_to_delete = DBBookGenre.query.filter_by(book_id=self.book_id, genre_id=self.genre_id).first()

            # Проверка, существует ли запись
            if record_to_delete:
                # Удаление записи
                db.session.delete(record_to_delete)
                # Сохранение изменений
                db.session.commit()
                print(f"Запись удалена: {record_to_delete}")
            else:
                print("Запись не найдена.")
        except Exception as e:
            # Откат изменений в случае ошибки
            db.session.rollback()
            print(f"Ошибка при удалении записи: {e}")
from api_v1 import db
# Инициализация SQLAlchemy
# db = SQLAlchemy(app)

class GenreModel(db.Model):
    __tablename__ = 'genres'

    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Genre(genre_id={self.genre_id}, name='{self.name}')>"
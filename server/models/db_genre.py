from sqlalchemy.orm import relationship

from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP

class DBGenre(db.Model):
    __tablename__ = 'genres'

    genre_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    books = relationship('DBBooks', secondary='book_genres', back_populates='genres')

    def __repr__(self):
        return f"<Genre {self.name} (ID: {self.genre_id})>"

    def to_json(self):
        return {
            "genreID": self.genre_id,
            "genreName": self.name
        }
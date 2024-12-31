from mysql.connector import  CMySQLConnection

from api_v1.db_data_returns import Genres
from api_v1.model_book_genres import BookGenreModel
from api_v1.model_genre import GenreModel
from api_v1 import db


def db_get_book_genres(book_id: int):
    genres_id = BookGenreModel.query.filter(BookGenreModel.book_id == book_id)
    result = []
    for item in genres_id.all():
        result.append(GenreModel.query.filter(GenreModel.genre_id == item.genre_id).first().name)
    return result


def db_get_all_genres():
    genres = GenreModel.query.all()
    result = []
    for item in genres:
        result.append(Genres.get_genre(item.genre_id, item.name))
    return result

def db_add_list_book_genres(book_id:int, genres_ids: list[int]):
    for item in genres_ids:
        new_genre = BookGenreModel(
            book_id = book_id,
            genre_id = item
        )
        db.session.add(new_genre)
    db.session.commit()

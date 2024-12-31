from mysql.connector import  CMySQLConnection
from api_v1.db_data_returns import Books
from api_v1.db_genres import db_get_book_genres
from api_v1.model_book import BookModel
from api_v1.model_book_genres import BookGenreModel
from api_v1.model_genre import GenreModel
from api_v1 import db




def get_catalog_books(limit: int = -1, offset: int = 0):
    """
    :param db_conn:
    :param limit:
    :param offset:
    :return:

    Необходимо: поиск по жанрам и поиск по названию и сортировка

    """
    result = {
        "book_list": [],
        "page": offset // limit if limit > 0 else 0,
        "count": 0
    }
    query_books = BookModel.query
    if limit > 0:
        query_books = query_books.limit(limit)
    if offset > 0:
        query_books = query_books.offset(offset)
    for item in query_books.all():
        book = Books.get_book(
            item.book_id,
            item.book_added_by,
            item.book_title,
            item.book_title_image,
            item.book_author,
            item.book_date_of_publication,
            item.book_rating,
            db_get_book_genres(item.book_id),
            item.book_description,
            item.book_isbn,
            item.created_at.strftime("%H:%M:%S %d-%m-%Y")
        )
        result["book_list"].append(book)
        result["count"] += 1

    return Books.get_catalog_book(
        result["book_list"],
        result["page"],
        result["count"]
    )


def get_catalog_book(book_id: int):
    book_db = BookModel.query.filter(BookModel.book_id == book_id)
    if not book_db:
        return None
    book = Books.get_book(
        book_db.book_id,
        book_db.book_added_by,
        book_db.book_title,
        book_db.book_title_image,
        book_db.book_author,
        book_db.book_date_of_publication,
        book_db.book_rating,
        db_get_book_genres(book_db.book_id),
        book_db.book_description,
        book_db.book_isbn,
        book_db.created_at.strftime("%H:%M:%S %d-%m-%Y")
    )
    return book

def db_append_book(
        book_added_by: int,
        book_title: str,
        book_title_image: str,
        book_author: str,
        book_date_of_publication: str,
        book_rating: int,
        book_description: str,
        book_isbn: str
) -> BookModel:
    new_book = BookModel(
        book_added_by = book_added_by,
        book_title = book_title,
        book_title_image = book_title_image,
        book_author = book_author,
        book_date_of_publication = book_date_of_publication,
        book_rating = book_rating,
        book_description = book_description,
        book_isbn = book_isbn
    )
    db.session.add(new_book)
    db.session.commit()
    return new_book
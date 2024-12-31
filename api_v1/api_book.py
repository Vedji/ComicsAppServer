from flask import jsonify, request
import api_v1.db_book
from api_v1 import bp
from api_v1.db_book import get_catalog_book
from api_v1.db_data_returns import Books
from api_v1.db_genres import db_add_list_book_genres
from api_v1.errors import BooksCatalogErrors
from api_v1.model_book import BookModel
from api_v1 import db


@bp.route('/api/v1/catalog/books', methods=["GET"])
def api_get_catalog_books():
    """ Список книг в каталоге """
    limit = request.args.get("limit", -1, int)
    offset = request.args.get("offset", -1, int)
    data = api_v1.db_book.get_catalog_books(limit, offset)
    return jsonify(data)

@bp.route('/api/v1/catalog/book', methods=["GET"])
def api_get_catalog_book():
    """ Информация о книги"""
    book_id = request.args.get("book_id", -1, int)
    data = api_v1.db_book.get_catalog_book(book_id)
    if data:
        return jsonify(data)
    return BooksCatalogErrors.book_not_found(book_id)

@bp.route('/api/v1/book/upload', methods=["POST"])
def api_upload_book_info():
    data = request.get_json()
    book_added_by = data.get("bookAddedBy")
    book_title = data.get("bookTitle")
    book_title_image = data.get("bookTitleImage")
    book_author = data.get("bookAuthor")
    book_date_of_publication = data.get("bookDateOfPublication")
    book_rating = data.get("bookRating")
    book_description = data.get("bookDescription")
    book_isbn = data.get("bookIsbn")
    book_genres = data.get("bookGenres")
    file = request

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
    db_add_list_book_genres(new_book.book_id, book_genres)
    return get_catalog_book(new_book.book_id)





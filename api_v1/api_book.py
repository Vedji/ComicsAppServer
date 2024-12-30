from flask import jsonify, request
import api_v1.db_book
from api_v1 import conn
from api_v1 import bp
from api_v1.errors import BooksCatalogErrors


@bp.route('/api/v1/catalog/books', methods=["GET"])
def api_get_catalog_books():
    """ Список книг в каталоге """
    limit = request.args.get("limit", -1, int)
    offset = request.args.get("offset", -1, int)
    return jsonify(api_v1.db_book.get_catalog_books(conn, limit, offset))

@bp.route('/api/v1/catalog/book', methods=["GET"])
def api_get_catalog_book():
    """ Информация о книги"""
    book_id = request.args.get("book_id", -1, int)
    data = api_v1.db_book.get_catalog_book(conn, book_id)
    if data:
        return jsonify(data)
    return BooksCatalogErrors.book_not_found(book_id)

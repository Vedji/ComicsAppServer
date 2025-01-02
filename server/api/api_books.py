import os.path
from re import search

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_

from server import Config
from server.api.extensions import ExtensionsReturned
from server.models.db_books import DBBooks
from server.models.db_files import DBFiles
from server.models.db_users import DBUser
from server.models.db_genre import DBGenre
from server.models.db_book_genres import DBBookGenre
from server import db

book_api = Blueprint('book_api', __name__)


@book_api.route('/v1/books/<int:book_id>/info', methods=['GET'])
def get_book_info(book_id: int):
    book = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if book:
        return jsonify(book.to_json()), 200

    return ExtensionsReturned.not_found("book_id", book_id)


@book_api.route('/v1/books/<int:book_id>/getGenres', methods=['GET'])
def get_book_genres(book_id: int):
    book = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not book:
        return ExtensionsReturned.not_found("Book", book_id)
    result = []
    genres = DBBooks.query.filter_by(book_id=book_id).first()
    for genre_book in genres.genres:
        result.append(genre_book.name)
    return jsonify({
        "bookID": book_id,
        "genreList": result
    }), 200


@book_api.route('/v1/books/catalog', methods=['GET'])
def get_book_list():
    arg_limit = request.args.get("limit", 10, int)
    arg_offset = request.args.get("offset", 0, int)
    arg_search = request.args.get("search", '', str)
    arg_sort_by = request.args.get("sortBy", '', str)
    genres_id = request.args.getlist('genreID', int)

    catalog_query = DBBooks.query

    # Поиск по названию и описанию
    if arg_search and len(arg_search) >= 3:
        catalog_query = catalog_query.filter(
            or_(
                DBBooks.book_title.like(f"%{arg_search}%"),
                DBBooks.book_description.like(f"%{arg_search}%")
            )
        )
    #
    if genres_id:
        catalog_query = (
            catalog_query
            .join(DBBookGenre, DBBooks.book_id == DBBookGenre.book_id)
            .join(DBGenre, DBBookGenre.genre_id == DBGenre.genre_id)
            .filter(DBGenre.genre_id.in_(genres_id))
        )

    if arg_sort_by == "ratingASC":  # по возрастанию рейтинга
        catalog_query = catalog_query.order_by(DBBooks.book_rating.asc())
    if arg_sort_by == "ratingDESC":  # по убыванию рейтинга
        catalog_query = catalog_query.order_by(DBBooks.book_rating.desc())
    if arg_sort_by == "titleASC":  # по возрастанию названия
        catalog_query = catalog_query.order_by(DBBooks.book_title.asc())
    if arg_sort_by == "titleDESC":  # по убыванию названия
        catalog_query = catalog_query.order_by(DBBooks.book_title.desc())
    if arg_sort_by == "publishedASC":  # по возрастанию дате написания
        catalog_query = catalog_query.order_by(DBBooks.book_date_publication.asc())
    if arg_sort_by == "publishedDESC":  # по убыванию дате написания
        catalog_query = catalog_query.order_by(DBBooks.book_date_publication.desc())
    if arg_sort_by == "addedASC":  # по возрастанию дате добавления
        catalog_query = catalog_query.order_by(DBBooks.created_at.asc())
    if arg_sort_by == "addedDESC":  # по убыванию названия дате добавления
        catalog_query = catalog_query.order_by(DBBooks.created_at.desc())


    if arg_offset:
        catalog_query = catalog_query.offset(arg_offset)
    if arg_limit:
        catalog_query = catalog_query.limit(arg_limit)

    result = []
    for item in catalog_query.all():
        result.append(item.to_json())

    return jsonify(
        DBBooks.catalog_to_json(
            result,
            arg_offset // arg_limit if arg_limit > 0 else 0,
            len(result)
        )
    ), 200








@book_api.route('/v1/books/<int:book_id>/setGenres', methods=['POST'])
@jwt_required()
def set_book_genres(book_id: int):
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)



    book_genres_id = request.form.getlist("bookGenreID", int)

    checked = DBGenre.query.filter(DBGenre.genre_id.in_(book_genres_id)).all()
    if len(checked) != len(book_genres_id):
        return ExtensionsReturned.invalid_field("book_genres_id", str(book_genres_id))

    buffer = DBBookGenre.query.filter(DBBookGenre.book_id == book_id).all()
    for item in buffer:
        item.delete_book_genre()

    for genre_id in book_genres_id:
        DBBookGenre(book_id=book_id, genre_id=genre_id).add_row()


    return jsonify({
        "bookID": book_id,
        "genreList": list(map(lambda x: x.name, DBGenre.query.filter(DBGenre.genre_id.in_(book_genres_id)).all()))
    }), 200













@book_api.route('/v1/books/upload', methods=['POST'])
@jwt_required()
def upload_file():
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id)

    book_title = request.form.get("bookTitle")
    book_date_publication = request.form.get("bookDatePublication")
    book_description = request.form.get("bookDescription")
    book_isbn = request.form.get("bookISBN")

    if not book_title:
        return ExtensionsReturned.invalid_field("bookTitle", book_title)
    if not book_date_publication:
        return ExtensionsReturned.invalid_field("bookDatePublication", book_date_publication)
    if not book_description:
        return ExtensionsReturned.invalid_field("bookDescription", book_description)
    if not book_isbn:
        return ExtensionsReturned.invalid_field("bookISBN", book_isbn)


    new_book = DBBooks(
        book_added_by =  current_user_id,
        book_title = book_title,
        book_date_publication = book_date_publication,
        book_description = book_description,
        book_isbn = book_isbn
    )
    if not new_book.add_book():
        return ExtensionsReturned.upload_error("DBBooks", new_book.__str__())
    file_path = Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY + f"\\manga\\book_{new_book.book_id}\\"
    if os.path.exists(file_path) and os.path.isdir(file_path):
        os.rmdir(file_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.rmdir(file_path)
    os.mkdir(file_path)

    file = request.files['bookTitleImage']
    if not file or file.filename == '':
        return ExtensionsReturned.invalid_field("bookTitleImage", "no value")
    file.save(file_path + f"timage.{file.mimetype.split('/')[-1]}")
    file_row = DBFiles(
        added_by = current_user_id,
        file_path =  f"manga\\book_{new_book.book_id}\\",
        file_name = f"timage.{file.mimetype.split('/')[-1]}",
        file_type = file.mimetype
    )
    if not file_row.add_file():
        return ExtensionsReturned.upload_error("DBFiles", file_row)
    try:
        new_book.book_title_image = file_row.file_id
        db.session.commit()
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
        db.session.rollback()
        return ExtensionsReturned.upload_error("DBFiles", file_row)
    return jsonify(new_book.to_json())
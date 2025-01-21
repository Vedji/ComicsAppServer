import os.path
import pprint
from re import search

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_

from server import Config
from server.api.extensions import ExtensionsReturned
from server.models.db_book_chapter import DBBookChapters
from server.models.db_books import DBBooks
from server.models.db_files import DBFiles
from server.models.db_users import DBUser
from server.models.db_genre import DBGenre
from server.models.db_book_genres import DBBookGenre
from server import db
from server.exceptions import *
from server.api_response import ApiResponse

book_api = Blueprint('book_api', __name__)
register_error_handlers(book_api)


@book_api.route('/v1/books/<int:book_id>/info', methods=['GET'])
def get_book_info(book_id: int):
    book = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if book:
        return jsonify(book.to_json()), 200
    raise NotFound("Book", "", 404, book_id = book_id)











@book_api.route('/v1/books/<int:book_id>/getGenres', methods=['GET'])
def get_book_genres(book_id: int):
    book = DBBooks.query.filter_by(book_id = book_id).first()
    if not book:
        raise NotFound("Book", "", 404, book_id = book_id)
    return jsonify({
        "bookID": book_id,
        "genreList": list(map(lambda x: x.name, book.genres))
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

    total_items_count = len(catalog_query.all())

    if arg_offset:
        catalog_query = catalog_query.offset(arg_offset)
    if arg_limit:
        catalog_query = catalog_query.limit(arg_limit)

    result = []
    for item in catalog_query.all():
        result.append(item.to_json())

    return jsonify(
        DBBooks.list_to_json(
            result,
            arg_offset // arg_limit if arg_limit > 0 else 0,
            len(result),
            total_items_count
        )
    ), 200


# Test apis
@book_api.route('/v1/books/<int:book_id>/setGenres', methods=['POST'])
@jwt_required()
def set_book_genres(book_id: int):
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        raise NotFound("User", "", 404, user_id=current_user_id)
    if not book_edit:
        raise NotFound("Book", "", 404, book_id=book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        raise NotPermission(
            "SetBookGenres",
            f"<User(user_id = {user_who_added.user_id}, permission = {user_who_added.permission})> "
            f"has not permission to set genres for Book(book_id = {book_id})"
        )

    book_genres_id = request.form.getlist("bookGenreID", int)

    checked = DBGenre.query.filter(DBGenre.genre_id.in_(book_genres_id)).all()
    if len(checked) != len(book_genres_id):
        raise InvalidField("book_genres_id", book_genres_id)

    buffer = DBBookGenre.query.filter(DBBookGenre.book_id == book_id).all()
    for item in buffer:
        item.delete_book_genre()

    for genre_id in book_genres_id:
        DBBookGenre(book_id=book_id, genre_id=genre_id).add_row()

    try:
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        raise DeleteError(
            "Book",
            err.__repr__(),
            500,
            book_id=current_user_id
        )

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
        book_added_by =  user_who_added.user_id,
        book_title = book_title,
        book_date_publication = book_date_publication,
        book_description = book_description,
        book_isbn = book_isbn
    )
    if not new_book.add_book():
        return ExtensionsReturned.upload_error("DBBooks", new_book.__str__())
    file_path = Config.linux_path(Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY + f"\\manga\\book_{new_book.book_id}\\")
    if os.path.exists(file_path) and os.path.isdir(file_path):
        os.rmdir(file_path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        os.rmdir(file_path)
    os.mkdir(file_path)

    file = request.files['bookTitleImage']
    if not file or file.filename == '':
        return ExtensionsReturned.invalid_field("bookTitleImage", "no value")
    file.save(Config.linux_path(file_path + f"timage.{file.mimetype.split('/')[-1]}"))
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



# Api v2


@book_api.route('/v2/books', methods=['GET'])
def get_book_list_v2():
    try:
        arg_limit = request.args.get("limit", 10, int)
        arg_offset = request.args.get("offset", 0, int)
        arg_search = request.args.get("search", '', str)
        arg_sort_by = request.args.get("sortBy", '', str)
        genres_id = request.args.getlist('genreId', int)
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
        total_items_count = len(catalog_query.all())
        if arg_offset:
            catalog_query = catalog_query.offset(arg_offset)
        if arg_limit:
            catalog_query = catalog_query.limit(arg_limit)
        result = []
        for item in catalog_query.all():
            result.append(item.to_json())
        return ApiResponse(
            data = result,
            metadata = ApiResponse.pagination(arg_limit, arg_offset, total_items_count)
        ).to_response()
    except CustomException as error:
        return error.to_response()


@book_api.route('/v2/books/<int:book_id>', methods=['GET'])
def get_book_info_v2(book_id: int):
    book = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if book:
        return ApiResponse(book.to_json()).to_response()
    raise NotFound("Book", "")


@book_api.route('/v2/books', methods=['PUT'])
@jwt_required()
def update_books_v2():
    try:
        current_user_id = get_jwt_identity()
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        if user_who_request.permission < 1:
            raise NotPermission("upload file")

        request_book_id = request.form.get("bookId", -1, int)
        request_book_title = request.form.get("bookName", "", str)
        request_book_genres: list[int] = request.form.getlist("bookGenres", int)
        request_book_description: str = request.form.get("bookDescription", "", str)
        request_book_date_of_publication: str = request.form.get("bookDateOfPublication", "", str)
        request_book_title_image_id: int = request.form.get("bookTitleImageId", -1, int)
        request_new_chapter_seq = request.form.getlist("bookChaptersSequence", int)

        print("request_book_id = ", request_book_id)
        print("request_book_title = ", request_book_title)
        print("request_book_genres = ", request_book_genres)
        print("request_book_description = ", request_book_description)
        print("request_book_date_of_publication = ", request_book_date_of_publication)
        print("request_book_title_image_id = ", request_book_title_image_id)
        print("request_new_chapter_seq = ", request_new_chapter_seq)


        if request_book_id <= 0:
            book = DBBooks(
            book_added_by = user_who_request.user_id,
            book_title = "New book",
            book_title_image = 4,
            book_date_publication = "YYYY-mm-dd HH:MM:SS",
            book_description = "New book description",
            book_isbn = " - "
            )
            db.session.add(book)
            db.session.commit()
        else:
            book: DBBooks = DBBooks.query.filter(DBBooks.book_id == request_book_id).first()
        if not book:
            raise NotFound("DBBooks", request_book_id)
        if request_book_genres:
            deleted_genres = DBBookGenre.query.filter(DBBookGenre.book_id == book.book_id).all()
            for i in deleted_genres:
                db.session.delete(i)
            db.session.commit()
            for g_id in request_book_genres:
                db.session.add(DBBookGenre(
                    book_id = book.book_id,
                    genre_id = g_id,
                ))
        if request_book_title:
            book.book_title = request_book_title
        if request_book_description:
            book.book_description = request_book_description
        if request_book_date_of_publication:
            book.book_date_publication = request_book_date_of_publication
        if request_book_title_image_id and request_book_title_image_id > 20:
            book.book_title_image = request_book_title_image_id
        if request_new_chapter_seq:
            chapters: list[DBBookChapters] = book.chapters
            for i in range(len(request_new_chapter_seq)):
                buffer_chapter_id = request_new_chapter_seq[i]
                buffer = list(filter(lambda x: buffer_chapter_id == x.chapter_id, chapters))
                if not buffer:
                    raise NotFound("DBComment", str(request_new_chapter_seq[i]))
                buffer: DBBookChapters = buffer[0]
                buffer.chapter_number = i
            book.chapters = chapters
        db.session.commit()
        return ApiResponse(book.to_json()).to_response()
    except CustomException as error:
        db.session.rollback()
        print(error)
        return error.to_response()
    except Exception as err:
        db.session.rollback()
        print(err)
        return CustomException(
            message=err.__repr__(),
            error=err.__class__
        ).to_response()
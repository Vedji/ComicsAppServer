import glob
import logging
import mimetypes
import os.path
import pprint
from re import search
import shutil
from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import or_, not_

from server import Config
from server.api.extensions import ExtensionsReturned
from server.exceptions import *
from server.models.db_books import DBBooks
from server.models.db_chapter_pages import DBChapterPages
from server.models.db_files import DBFiles
from server.models.db_users import DBUser
from server.models.db_genre import DBGenre
from server.models.db_book_genres import DBBookGenre
from server.models.db_book_chapter import DBBookChapters
from server import db

book_chapter_pages_api = Blueprint('book_chapter_pages_api', __name__)


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages', methods=['GET'])
def get_book_chapter_pages_list(book_id: int, chapter_id: int):
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    chapter = chapter[0]
    if not chapter.pages:
        return jsonify({
            "pagesList": [],
            "chapterLength": 0
        }), 200
    pages = chapter.pages
    print(pages)
    pages.sort(key = lambda x: x.page_number)
    pages = list(map(lambda x: x.to_json(), pages))
    return jsonify({
        "pagesList": pages,
        "chapterLength": chapter.chapter_length
    }), 200


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages/<int:page_id>', methods=['GET'])
def get_book_chapter_page(book_id: int, chapter_id: int, page_id: int):
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    chapter = chapter[0]
    pages = chapter.pages
    if not pages:
        return ExtensionsReturned.not_found(
            "DBChapterPages", f"book_id = {book_id}, chapter_id = {chapter_id}, page_id = {page_id}"
        )
    page = list(filter(lambda x: x.chapter_id == chapter_id, pages))
    if not page:
        return ExtensionsReturned.not_found(
            "DBChapterPages", f"book_id = {book_id}, chapter_id = {chapter_id}, page_id = {page_id}"
        )
    return jsonify(page[0].to_json()), 200


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages', methods=['POST'])
@jwt_required()
def add_book_chapter_page(book_id: int, chapter_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    if 'file' not in request.files:
        return ExtensionsReturned.invalid_field("file", "None")
    file = request.files['file']
    if file.filename == '' or not file:
        return ExtensionsReturned.invalid_field("file", "None")

    chapter = chapter[0]
    try:
        added_page = DBChapterPages(
            chapter_id = chapter_id,
            page_number = len(chapter.pages),
            added_by = user_who_added.user_id
        )
        db.session.add(added_page)
        db.session.commit()
        file_pattern = (f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga"
                    f"\\book_{book_edit.book_id}\\chapter_{chapter_id}\\page_{added_page.page_id}.*")
        for file_path in glob.glob(file_pattern):
            print("DELETED: ", file_path)
            os.remove(file_path)
        file.save(Config.linux_path(
            f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga\\book_{book_edit.book_id}"
            f"\\chapter_{chapter_id}\\page_{added_page.page_id}." + file.filename.split('.')[-1]
        ))
        new_file = DBFiles(
            added_by = user_who_added.user_id,
            file_path = f"manga\\book_{book_edit.book_id}\\chapter_{chapter_id}\\",
            file_name = f"page_{added_page.page_id}." + file.filename.split('.')[-1],
            file_type = file.mimetype
        )
        db.session.add(new_file)
        db.session.commit()
        added_page.page_image_id = new_file.file_id
        db.session.commit()

    except Exception as e:
        logging.error(f"Ошибка при записи: {e}, в модели {chapter.__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", e)
    chapter.pages.sort(key=lambda x: x.page_number)
    return jsonify(added_page.to_json()), 200


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages', methods=['PUT'])
@jwt_required()
def edit_book_chapter_pages_sequence(book_id: int, chapter_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    pages_id_seq = request.form.getlist("pagesID", int)
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    chapter = chapter[0]
    check_genre_ids = list(filter(lambda x: x not in map(lambda y: y.page_id, chapter.pages), pages_id_seq))
    if check_genre_ids:
        return ExtensionsReturned.invalid_field("pagesID", str(check_genre_ids))
    try:
        for i in range(len(pages_id_seq)):
            item_page = list(filter(lambda x: x.page_id == pages_id_seq[i], chapter.pages))
            if not item_page:
                return ExtensionsReturned.invalid_field("pagesID", str(pages_id_seq[i]))
            item_page[0].page_number = i
        db.session.commit()
    except Exception as e:
        logging.error(f"Ошибка при записи: {e}, в модели {chapter.__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", e)
    pages = list(map(lambda x: x.to_json(), sorted(chapter.pages, key=lambda x: x.page_number)))
    return jsonify({
        "pagesList": pages,
        "chapterLength": chapter.chapter_length
    }), 200


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages/<int:page_id>', methods=['PUT'])
@jwt_required()
def edit_book_chapter_page(book_id: int, chapter_id: int, page_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    pages_id_seq = request.form.getlist("pagesID", int)
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    page = list(filter(lambda x: x.page_id == page_id, chapter[0].pages))
    if not page:
        return ExtensionsReturned.invalid_field(
            "page_id", f"page_id = {page_id}"
        )
    page = page[0]
    if 'file' not in request.files:
        return ExtensionsReturned.invalid_field("file", "None")
    file = request.files['file']
    if file.filename == '' or not file:
        return ExtensionsReturned.invalid_field("file", "None")
    try:
        file_pattern = Config.linux_path((f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga"
                        f"\\book_{book_edit.book_id}\\chapter_{chapter_id}\\page_{page.page_id}.*"))
        for file_path in glob.glob(file_pattern):
            print("DELETED: ", file_path)
            os.remove(Config.linux_path(file_path))
        file.save(Config.linux_path(
            f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga\\book_{book_edit.book_id}"
            f"\\chapter_{chapter_id}\\page_{page.page_id}." + file.filename.split('.')[-1]
        ))
        new_file = DBFiles(
            added_by=user_who_added.user_id,
            file_path=f"manga\\book_{book_edit.book_id}\\chapter_{chapter_id}\\",
            file_name=f"page_{page.page_id}." + file.filename.split('.')[-1],
            file_type=file.mimetype
        )
        db.session.add(new_file)
        db.session.commit()
        page.page_image_id = new_file.file_id
        db.session.commit()

    except Exception as e:
        logging.error(f"Ошибка при записи: {e}, в модели {chapter.__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", e)
    return jsonify(page.to_json()), 200


@book_chapter_pages_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>/pages/<int:page_id>', methods=['DELETE'])
@jwt_required()
def delete_book_chapter_page(book_id: int, chapter_id: int, page_id: int):
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter = list(filter(lambda x: x.chapter_id == chapter_id, DBBooks.query.filter_by(book_id = book_id).first().chapters))
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    pages_id_seq = request.form.getlist("pagesID", int)
    # chapters = DBBooks.query.filter_by(book_id = book_id).first().chapters
    # chapters.sort(key=lambda x: x.chapter_number)
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    if not chapter:
        return ExtensionsReturned.not_found(
            "DBBookChapters", f"book_id = {book_id}, chapter_id = {chapter_id}"
        )
    page = list(filter(lambda x: x.page_id == page_id, chapter[0].pages))
    if not page:
        return ExtensionsReturned.invalid_field(
            "page_id", f"page_id = {page_id}"
        )
    page = page[0]
    deleted_pages = page.to_json()
    try:
        file_id = page.page_image_id
        file_row = DBFiles.query.filter_by(file_id = file_id).first()
        if not file_row:
            raise ValueError(f"file_id with id equals '{file_id}' is not exists!")
        file_path = file_row.file_path
        file_name = file_row.file_name

        db.session.delete(page)
        db.session.commit()

        if file_id > 20:
            db.session.delete(file_row)
            file_path = f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\{file_path}\\{file_name}"
            if os.path.exists(Config.linux_path(file_path)) and os.path.isfile(Config.linux_path(file_path)):
                print("DELETED: ", Config.linux_path(file_path))
                os.remove(Config.linux_path(file_path))
            else:
                raise ValueError(f"file_path = '{file_path}' error delete!")
            db.session.commit()

    except Exception as e:
        logging.error(f"Ошибка при удалении: {e}, в модели {page.__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", e)
    return jsonify(deleted_pages), 200


# Api v2
import time

@book_chapter_pages_api.route('/v2/books/<int:book_id>/chapters/<int:chapter_id>/pages', methods=['GET'])
def get_book_chapter_pages_list_v2(book_id: int, chapter_id: int):
    try:

        book: DBBooks = DBBooks.query.filter(DBBooks.book_id == book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        current_chapter: DBBookChapters = next(iter(filter(lambda x: x.chapter_id == chapter_id, book.chapters)), None)
        pprint.pprint(current_chapter)
        if not current_chapter:
            raise NotFound("DBBookChapters", chapter_id, "DBBookChapters not found")
        last_chapter: DBBookChapters = next(
            (item for item in book.chapters if item.chapter_number == (current_chapter.chapter_number - 1)), None)
        next_chapter: DBBookChapters = next(
            (item for item in book.chapters if item.chapter_number == (current_chapter.chapter_number + 1)), None)
        metadata = {
            "lastItemId": last_chapter.chapter_id if last_chapter else -1,
            "nextItemId": next_chapter.chapter_id if next_chapter else -1
        }
        return ApiResponse(
            data = [item.to_json() for item in current_chapter.pages],
            metadata = metadata
        ).to_response()
    except CustomException as error:
        return error.to_response()
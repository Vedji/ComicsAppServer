import logging
import os.path
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

book_chapters_api = Blueprint('book_chapters_api', __name__)


@book_chapters_api.route('/v1/books/<int:book_id>/chapters', methods=['GET'])
def get_book_chapters_list(book_id: int):

    book = DBBooks.query.filter_by(book_id = book_id).first()
    if not book:
        return ExtensionsReturned.invalid_field("book_id", str(book_id))
    book_chapters = list(map(lambda x: x.to_json(), book.chapters))
    book_chapters.sort(key = lambda x: x["chapterNumber"])
    return jsonify(DBBookChapters.to_list_json(book_chapters, len(book_chapters), 0)), 200

@book_chapters_api.route('/v2/books/<int:book_id>/chapters', methods=['GET'])
def get_book_chapters_list_2(book_id: int):
    try:
        book = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        if book and book.chapters:
            chapters = list(map(lambda chapter: chapter.to_json(), book.chapters))
            chapters.sort(key=lambda x: x["chapterNumber"])
            return ApiResponse(chapters).to_response()
        else:
            return ApiResponse([]).to_response()
    except CustomException as error:
        return error.to_response()


@book_chapters_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>', methods=['GET'])
def get_book_chapter(book_id: int, chapter_id: int):
    book = DBBooks.query.filter_by(book_id = book_id).first()
    if not book:
        return ExtensionsReturned.invalid_field("book_id", str(book_id))
    chapter = None
    for item in book.chapters:
        if item.chapter_id == chapter_id:
            chapter = item
            break
    if not chapter:
        return ExtensionsReturned.not_found("chapter", str(chapter_id))
    return jsonify(chapter.to_json()), 200


@book_chapters_api.route('/v2/books/<int:book_id>/chapters/<int:chapter_id>', methods=['GET'])
def get_book_chapter_v2(book_id: int, chapter_id: int):
    try:
        book = DBBooks.query.filter_by(book_id=book_id).first()
        if not book:
            raise NotFound("Book", book_id, "Book not found")
        if book and book.chapters:
            chapter = list(filter(lambda x: x.chapter_id == chapter_id, book.chapters))
            if chapter and chapter[0]:
                return ApiResponse(chapter[0].to_json()).to_response()
            raise NotFound("Chapter", book_id, "Chapter not found")
        else:
            return ApiResponse({}).to_response()
    except CustomException as error:
        return error.to_response()


@book_chapters_api.route('/v1/books/<int:book_id>/chapters', methods=['POST'])
@jwt_required()
def add_book_chapter(book_id: int):
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter_title = request.form.get("chapterTitle", None)
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    chapter_number = max(book_edit.chapters,key=lambda x: x.chapter_number).chapter_number + 1 if book_edit.chapters else 0
    new_chapter = DBBookChapters(
        book_id = book_id,
        chapter_title = chapter_title,
        chapter_number = chapter_number,
        added_by = int(current_user_id)
    )

    if not new_chapter.add_value():
        return ExtensionsReturned.upload_error("DBBookChapters", new_chapter.__repr__())
    work_dir = Config.linux_path(f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga"
                f"\\book_{book_edit.book_id}\\chapter_{new_chapter.chapter_id}\\")
    print(f"New chapter file path = '{work_dir}';")
    if os.path.exists(work_dir):
        shutil.rmtree(work_dir)
    os.mkdir(work_dir)
    print(f"New chapter file path = '{work_dir}', chapter_exists = {os.path.exists(work_dir)};")
    return jsonify(new_chapter.to_json()), 200


@book_chapters_api.route('/v1/books/<int:book_id>/chapters', methods=['PUT'])
@jwt_required()
def edit_book_chapter(book_id: int):
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()
    chapter_title = request.form.get("chapterTitle", None)
    chapter_title_id = request.form.get("chapterTitleID", None, int)
    chapter_seq = request.form.getlist("chapterID", int)
    if chapter_seq and (chapter_title or chapter_title_id):
        return ExtensionsReturned.invalid_field("chapterID or (chapterTitle and chapterTitleId)", f"{chapter_seq} or ({chapter_title} and {chapter_title_id})")
    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)

    # Edit chapter title
    if chapter_title:
        edit_chapter = DBBookChapters.query.filter_by(chapter_id = chapter_title_id).first()
        if not edit_chapter:
            return ExtensionsReturned.not_found("DBBookChapters", chapter_title_id)
        edit_chapter.chapter_title = chapter_title
        if not edit_chapter.set_value():
            return ExtensionsReturned.upload_error("DBBookChapters", edit_chapter.__repr__())
        return jsonify(edit_chapter.to_json()), 200

    # Edit chapters sequence
    edit_chapter = None
    edit_book_chapter_list = []
    try:
        for i in range(len(chapter_seq)):
            edit_chapter =  list(filter(lambda x: x.chapter_id == chapter_seq[i], book_edit.chapters))
            print(edit_chapter)
            if not edit_chapter:
                raise ValueError(f"DBBookChapters with id = {chapter_seq[i]} not found in books with id = {book_edit.book_id}")
            edit_chapter[0].chapter_number = i
        edit_book_chapter_list.append(edit_chapter)
        db.session.commit()
    except Exception as e:
        logging.error(f"Ошибка при записи: {e}, в модели {edit_chapter.__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", edit_chapter.__repr__())

    book_chapters = list(map(lambda x: x.to_json(), book_edit.chapters))
    book_chapters.sort(key=lambda x: x["chapterNumber"])
    return jsonify(DBBookChapters.to_list_json(book_chapters, len(book_chapters), 0)), 200


@book_chapters_api.route('/v1/books/<int:book_id>/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
def delete_book_chapter(book_id: int, chapter_id: int):
    # Получение текущего пользователя
    current_user_id = get_jwt_identity()
    user_who_added = DBUser.query.filter(DBUser.user_id == current_user_id).first()

    book_edit = DBBooks.query.filter(DBBooks.book_id == book_id).first()
    chapter_edit = list(filter(lambda x: x.chapter_id == chapter_id, book_edit.chapters))
    if not user_who_added:
        return ExtensionsReturned.not_found("DBUser", current_user_id)
    if not book_edit:
        return ExtensionsReturned.not_found("DBBooks", book_id)
    if book_edit.book_added_by != user_who_added.user_id and user_who_added.permission != 4:
        return ExtensionsReturned.not_permission(user_who_added.user_id, user_who_added.permission)
    if not chapter_edit:
        return ExtensionsReturned.not_found("DBBookChapters", chapter_id)

    print(chapter_edit)
    book_chapters_edit = book_edit.chapters
    deleted_chapter = chapter_edit[0].to_json()
    print(deleted_chapter)
    chapter_number = 0
    try:
        for i in range(len(book_chapters_edit)):
            if book_chapters_edit[i].chapter_id == chapter_edit[0].chapter_id:
                work_dir = (f"{Config.PROJECT_DIRECTORY + Config.DATA_DIRECTORY}\\manga"
                            f"\\book_{book_edit.book_id}\\chapter_{chapter_edit[0].chapter_id}\\")
                db.session.delete(chapter_edit[0])
                if os.path.exists(work_dir):
                    shutil.rmtree(work_dir)
                continue
            book_chapters_edit[i].chapter_number = chapter_number
            chapter_number += 1
        db.session.commit()
        return jsonify(deleted_chapter), 200
    except Exception as e:
        logging.error(f"Ошибка при удалении: {e}, в модели {chapter_edit[0].__repr__()}.")
        db.session.rollback()
        return ExtensionsReturned.upload_error("ExtensionsReturned", chapter_edit[0].__repr__())

# Api v2

# FIXME: Edit adding pages
@book_chapters_api.route('/v2/books/<int:book_id>/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
def update_book_chapter_v2(book_id: int, chapter_id: int):
    try:
        current_user_id = get_jwt_identity()
        user_who_request: DBUser = DBUser.query.filter(DBUser.user_id == current_user_id).first()
        if not user_who_request:
            raise NotFound(f"<User(user_id = {current_user_id})>")
        if user_who_request.permission < 1:
            raise NotPermission("upload file")
        book = DBBooks.query.filter(DBBooks.book_id == book_id).first()
        if not book:
            raise NotFound(f"DBBook(book_id = {book_id})")
        print(request.form)
        request_chapter_title = request.form.get("chapterTitle", "", str)
        request_pages_ids: list[int] = request.form.getlist("chapterPagesIds", int)
        request_pages_images_ids: list[int] = request.form.getlist("chapterPagesImageIds", int)

        print("request_chapter_title = ", request_chapter_title)
        print("request_pages_ids = ", request_pages_ids)
        print("request_pages_images_ids = ", request_pages_images_ids)

        chapter:DBBookChapters = DBBookChapters.query.filter(DBBookChapters.chapter_id == chapter_id).first()
        if not chapter:
            chapter:DBBookChapters = DBBookChapters(
                book_id = book_id,
                chapter_number = len(book.chapters),
                chapter_title = request_chapter_title,
                added_by = user_who_request.user_id
            )
            db.session.add(chapter)
            db.session.commit()
        chapter.chapter_title = request_chapter_title
        for page in list(filter(lambda x: x.chapter_id not in request_pages_ids, chapter.pages)):
            db.session.delete(page)
        for page_id in range(len(request_pages_ids)):
            pages = list(filter(lambda x: x.page_id == request_pages_ids[page_id], chapter.pages))
            if not pages and request_pages_ids[page_id] > 0:
                raise NotFound(f"DBBookChapters(page_id = {request_pages_ids[page_id]})")
            if not pages:
                page = DBChapterPages(
                    chapter_id = chapter.chapter_id,
                    page_number = page_id,
                    page_image_id = request_pages_images_ids[page_id],
                    added_by = user_who_request.user_id
                )
                db.session.add(page)
            else:
                pages[0].page_number = page_id
                pages[0].page_image_id = request_pages_images_ids[page_id]
        db.session.commit()
        return ApiResponse(chapter.to_json()).to_response()
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
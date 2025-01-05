import logging
import os.path
from re import search
import shutil
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
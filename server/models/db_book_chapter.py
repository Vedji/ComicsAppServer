from sqlalchemy.orm import relationship
from server.models.db_model import DBModel
from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP, DECIMAL, DateTime
from datetime import datetime
from server.models.db_chapter_pages import DBChapterPages


class DBBookChapters(db.Model, DBModel):
    __tablename__ = 'book_chapters'

    chapter_id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey('books.book_id'), nullable=False)
    chapter_title = Column(String(128), nullable=False, default='\u0413\u043b\u0430\u0432\u0430 \u2116')
    chapter_number = Column(Integer, nullable=False)
    chapter_length = Column(Integer, nullable=True, default=0)
    added_by = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)

    book = relationship('DBBooks', back_populates='chapters')
    pages = relationship('DBChapterPages', back_populates='chapter')
    favorites = relationship('DBUserFavorites', back_populates='chapter')

    def __repr__(self):
        return (f"<BookChapter(chapter_id={self.chapter_id}, chapter_title='{self.chapter_title}', "
                f"chapter_number={self.chapter_number}, book_id={self.book_id})>")

    def to_json(self) -> dict:
        return {
            "chapterID": self.chapter_id,
            "bookID": self.book_id,
            "chapterTitle": self.chapter_title,
            "chapterNumber": self.chapter_number,
            "chapterLength": self.chapter_length,
            "addedBy": self.added_by,
            "uploadDate": self.created_at.strftime(Config.DATE_FORMAT) if self.created_at else ""
        }

    @staticmethod
    def to_list_json(obj_list: list, count: int, page: int):
        return {
            "chaptersList": obj_list,
            "count": count,
            "page": page
        }
from sqlalchemy.orm import relationship
from server.models.db_model import DBModel
from server import db, Config
from sqlalchemy import Column, Integer, String, ForeignKey, Text, func, TIMESTAMP, DECIMAL, DateTime
from datetime import datetime


class DBChapterPages(db.Model, DBModel):
    __tablename__ = 'chapter_pages'

    page_id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('book_chapters.chapter_id'), nullable=False)
    page_number = Column(Integer, nullable=False)
    page_image_id = Column(Integer, nullable=False, default=6)
    added_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=True, default=datetime.utcnow)

    chapter = relationship('DBBookChapters', back_populates='pages')

    def __repr__(self):
        return (f"<ChapterPage(page_id={self.page_id}, page_number={self.page_number}, "
                f"chapter_id={self.chapter_id}, page_image_id={self.page_image_id})>")

    def to_json(self) -> dict:
        return {
            "pageID": self.page_id,
            "chapterID": self.chapter_id,
            "pageNumber": self.page_number,
            "pageImageID": self.page_image_id,
            "addedBy": self.added_by,
            "uploadDate": self.created_at.strftime(Config.DATE_FORMAT) if self.created_at else ""
        }

    @staticmethod
    def to_list_json(obj_list: list, count: int, page: int):
        return {
            "chapterPagesList": obj_list,
            "count": count,
            "page": page
        }
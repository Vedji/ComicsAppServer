from sqlalchemy import Column, Integer

from server import db
import logging


class DBModel:

    def to_json(self) -> dict:
        return {}

    @staticmethod
    def to_list_json(obj_list: list, count: int, page: int):
        return {
            "listObjects": obj_list,
            "page": page,
            "count": count
        }

    def add_value(self) -> bool:
        try:
            db.session.add(self)
            db.session.commit()
            logging.info(f"Запись модели {self.__repr__()}")
        except Exception as e:
            logging.error(f"Ошибка при записи: {e}, в модели {type(self.__repr__())}.")
            db.session.rollback()
            return False
        return True

    def set_value(self):
        try:
            db.session.commit()
            logging.info(f"Изменение модели {self.__repr__()}")
        except Exception as e:
            logging.error(f"Ошибка при изменение записи: {e}, в модели {type(self.__repr__())}.")
            db.session.rollback()
            return False
        return True

    @staticmethod
    def remove_value(self):
        try:
            logging.info(f"Удаление модели {self.__repr__()}")
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка при удалении записи: {e}, в модели {type(self)}.")
            return False
        return True

    def __repr__(self):
        return f"DBModel(type = {type(self)})"


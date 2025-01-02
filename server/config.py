import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = ''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10                           # Размер пула соединений
    SQLALCHEMY_POOL_TIMEOUT = 120                       # Таймаут соединений
    SQLALCHEMY_POOL_RECYCLE = 100                       # Рецикл соединений
    SQLALCHEMY_MAX_OVERFLOW = 5                         # Допустимое превышение пула
    SQLALCHEMY_ENGINE_OPTIONS = { 'pool_pre_ping': True }

    JWT_SECRET_KEY = ''
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    @staticmethod
    def linux_path(path: str) -> str:
        path = path.replace('\\', '/', -1)
        return path

    DATE_FORMAT = "%H:%M:%S %d-%m-%Y"
    PROJECT_DIRECTORY = os.getcwd()
    DATA_DIRECTORY = '/data'




    @staticmethod
    def load_config(file_name: str = 'config.txt'):
        # if not os.path.exists(os.getcwd() + "\\" + file_name):
        #     return

        file = open(Config.linux_path(os.getcwd() + "\\" + file_name), 'r', encoding='utf-8')
        for line in file.readlines():
            line = line.replace('\n', '', -1)
            line = line.replace(' ', '', -1)
            line = line.replace('\t', '', -1)
            comment_index = line.find("#")
            if comment_index >= 0:
                line = line[:comment_index]
            if line.find("===") < 0:
                continue
            field, value = line.split("===")
            if 'SQLALCHEMY_DATABASE_URI' in field:
                Config.SQLALCHEMY_DATABASE_URI = value
                print(f"filed = '{field}', value = '{value}'")
            if 'JWT_SECRET_KEY' in field:
                Config.JWT_SECRET_KEY = value
                print(f"filed = '{field}', value = '{value}'")
            if 'PROJECT_DIRECTORY' in  field:
                Config.PROJECT_DIRECTORY = Config.linux_path(value)
                print(f"filed = '{field}', value = '{Config.linux_path(value)}'")
            if 'DATA_DIRECTORY' in field:
                Config.DATA_DIRECTORY = Config.linux_path(value)
                print(f"filed = '{field}', value = '{Config.linux_path(value)}'")
            if 'DATE_FORMAT' in field:
                Config.DATE_FORMAT = value
                print(f"filed = '{field}', value = '{value}'")
            if 'SQLALCHEMY_TRACK_MODIFICATIONS' in field:
                Config.SQLALCHEMY_TRACK_MODIFICATIONS = bool(int(value))
                print(f"filed = '{field}', value = '{bool(int(value))}'")
            if 'SQLALCHEMY_POOL_SIZE' in field:
                Config.SQLALCHEMY_POOL_SIZE = int(value)
                print(f"filed = '{field}', value = '{int(value)}'")
            if 'SQLALCHEMY_POOL_TIMEOUT' in field:
                Config.SQLALCHEMY_POOL_TIMEOUT  = int(value)
                print(f"filed = '{field}', value = '{int(value)}'")
            if 'SQLALCHEMY_POOL_TIMEOUT' in field:
                Config.SQLALCHEMY_POOL_TIMEOUT  = int(value)
                print(f"filed = '{field}', value = '{int(value)}'")
            if 'SQLALCHEMY_POOL_RECYCLE ' in field:
                Config.SQLALCHEMY_POOL_RECYCLE   = int(value)
                print(f"filed = '{field}', value = '{int(value)}'")

        file.close()
        # for i in file.read():
        #     print(file)


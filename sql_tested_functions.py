import mysql.connector
my_admin_id = 1


def add_file(file_name: str, file_type: str, file_path: str, added_by: int = 1, ) -> None:
    sql = """
    INSERT INTO files (added_by, file_name, file_type, file_content)
    VALUES (%s, %s, %s, %s)
    """
    with open(file_path, 'rb') as file:
        file_content = file.read()
    cursor = conn.cursor()
    cursor.execute(sql, (added_by, file_name, file_type, file_content))
    conn.commit()
    cursor.close()

def get_genres():
    sql = "SELECT * FROM genres;"
    cursor = conn.cursor()
    cursor.execute(sql)
    print(cursor.fetchall())
    cursor.close()


def kill_clone_conn():
    sql = "SELECT CONCAT('KILL ', id, ';') FROM information_schema.PROCESSLIST WHERE user = 'comicsappdb' and id != 29857;"
    cursor = conn.cursor()
    cursor.execute(sql)
    for i in list(map(lambda x: x[0], cursor.fetchall())):
        print(i)
    cursor.close()

if __name__ == '__main__':
    conn = mysql.connector.connect(
        host="85.192.49.28",  # Адрес сервера MySQL (может быть IP-адрес или доменное имя)
        user="comicsappdb",  # Ваше имя пользователя MySQL
        password="0*9%/e0E1&m9f2",  # Ваш пароль от MySQL
        database="ComicsAppDB"  # Имя базы данных, к которой вы хотите подключиться
    )
    kill_clone_conn()
    # get_genres()
    # add_file("timage_onepunchman.jpg", 'image/jpeg', 'data/timage/timage_onepunchman.jpg')
    # add_file("file_not_found.jpg", 'image/jpeg', 'data/file_not_found.jpg')
    conn.close()
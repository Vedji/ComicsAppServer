from mysql.connector import  CMySQLConnection



def get_catalog_books(db_conn: CMySQLConnection, limit: int = -1, offset: int = 0):
    result = {
        "book_list": [],
        "page": offset // limit if limit > 0 else 0,
        "count": 0
    }
    cursor = db_conn.cursor()
    sql_book = (f"""SELECT * FROM books""" +
           (f" LIMIT {limit}" if limit > 0 else "")
           + (f" OFFSET {offset}" if offset > 0 else "") + ";")
    cursor.execute(sql_book)
    book_info_list = cursor.fetchall()
    for item in book_info_list:
        book = {
            "book_id": item[0],
            "book_title": item[2],
            "book_author": item[4],
            "book_date_of_publication": item[5],
            "book_rating": item[6],
            "book_genres": [],
            "book_description": item[7],
            "book_isbn": item[8],
            "book_added_at": item[9].strftime("%H:%M:%S %d-%m-%Y")
        }
        sql_genres = f"""SELECT name FROM genres WHERE genre_id in 
        (SELECT genre_id FROM book_genres WHERE book_id = {item[0]});"""
        cursor.execute(sql_genres)
        genres = cursor.fetchall()
        book["book_genres"] = list(map(lambda x: x[0], genres))
        result["book_list"].append(book)
        result["count"] += 1

    db_conn.commit()
    cursor.close()
    print(result)
    return result

def get_catalog_book(db_conn: CMySQLConnection, book_id: int):
    cursor = db_conn.cursor()
    sql_book = f"""SELECT * FROM books WHERE book_id = {book_id};"""
    cursor.execute(sql_book)
    book_db = cursor.fetchone()
    cursor.reset()
    sql_genres = f"""SELECT name FROM genres WHERE genre_id in 
        (SELECT genre_id FROM book_genres WHERE book_id = {book_id});"""
    cursor.execute(sql_genres)
    book_db_genres = cursor.fetchall()
    cursor.close()
    result = {
        "book_id": book_db[0],
        "book_added_by": book_db[1],
        "book_title": book_db[2],
        "book_title_image": book_db[3],
        "book_author": book_db[4],
        "book_date_of_publication": book_db[5],
        "book_rating": book_db[6],
        "book_description": book_db[7],
        "book_isbn": book_db[8],
        "book_added_at": book_db[9].strftime("%H:%M:%S %d-%m-%Y"),
        "book_genres": list(map(lambda x: x[0], book_db_genres))
    }
    print(result)
    return result if book_db else None
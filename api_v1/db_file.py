from mysql.connector import  CMySQLConnection


def get_file(db_conn: CMySQLConnection, file_id: int):
    cursor = db_conn.cursor()
    sql = f"""SELECT * FROM files WHERE file_id = {file_id};"""
    cursor.execute(sql)
    data = cursor.fetchone()
    if data:
        result = {
            "file_name": data[2],
            "file_type": data[3],
            "file_content": data[5]
        }
        return result
    sql = f"""SELECT * FROM files WHERE file_id = 4;"""
    cursor.execute(sql)
    data = cursor.fetchone()
    result = {
        "file_name": data[2],
        "file_type": data[3],
        "file_content": data[5]
    }
    cursor.close()
    return result


def get_file_info(db_conn: CMySQLConnection, file_id: int):
    cursor = db_conn.cursor()
    sql = f"""SELECT file_id, added_by, file_name, file_type, upload_date FROM files WHERE file_id = {file_id};"""
    cursor.execute(sql)
    data = cursor.fetchone()
    cursor.close()
    if data:
        return {
            "file_id": data[0],
            "added_by": data[1],
            "file_name": data[2],
            "file_type": data[3],
            "upload_date": data[4].strftime("%H:%M:%S %d-%m-%Y")
        }
    return None



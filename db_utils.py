import sqlite3


def connect_to_db(db_file):
    return sqlite3.connect(db_file)


def fetchall_from_query(db_file, query, *params):
    conn = connect_to_db(db_file)
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall()
    return data

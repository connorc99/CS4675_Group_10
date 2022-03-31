import sqlite3
from sqlite3 import Error
import time

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None

    conn = sqlite3.connect(db_file)
    print(sqlite3.version)
    return conn


conn = create_connection('urldatabase.db')
cur = conn.cursor()
cur.execute('select * from urls')
print(cur.fetchall())
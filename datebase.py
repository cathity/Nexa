import sqlite3

DB_NAME = "nexa.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        reset_code TEXT,
        reset_code_expires INTEGER
                );
                """)


    try:
        cur.execute("ALTER TABLE users ADD COLUMN reset_code_expires INTEGER")
        print("Dodano kolumnę reset_code_expires")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
init_db()
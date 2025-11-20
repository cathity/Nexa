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
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            reset_code TEXT,
            reset_code_expires INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
                """)

    cur.execute("""
      CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
          )
    """)
    try:
        cur.execute("ALTER TABLE users ADD COLUMN reset_code_expires INTEGER")
        print("Dodano kolumnę reset_code_expires")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()
init_db()

import sqlite3
import os

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
            reset_code_expires INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            email_verified INTEGER DEFAULT 0,          
            email_verification_code TEXT,             
            verification_code_expires INTEGER        
        );
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

    cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    event_date DATE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)

    try:
        cur.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
        print("Dodano kolumnę email_verified")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN email_verification_code TEXT")
        print("Dodano kolumnę email_verification_code")
    except sqlite3.OperationalError:
        pass

    try:
        cur.execute("ALTER TABLE users ADD COLUMN verification_code_expires INTEGER")
        print("Dodano kolumnę verification_code_expires")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


init_db()

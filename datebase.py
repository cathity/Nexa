# database.py
import os
import sys

#dostęp do PostgreSQL
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    CLOUD_DB = True
    print("✓ PostgreSQL dostępny - tryb chmurowy")
except ImportError:
    import sqlite3

    CLOUD_DB = False
    print("ℹ PostgreSQL niedostępny - tryb lokalny (SQLite)")


def get_connection():
    if CLOUD_DB:
        try:
            #Railway automatycznie ustawia DATABASE_URL
            DATABASE_URL = os.environ.get('DATABASE_URL')

            if not DATABASE_URL:
                print("✗ DATABASE_URL nie ustawiony - przełączam na SQLite")
                return sqlite3.connect("nexa_local.db")

            #Połączenie z PostgreSQL na Railway
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            print("✓ Połączono z PostgreSQL na Railway")
            return conn

        except Exception as e:
            print(f"✗ Błąd połączenia z PostgreSQL: {e}")
            print("ℹ Przełączam na SQLite lokalnie")
            return sqlite3.connect("nexa_local.db")
    else:
        #Tryb lokalny - SQLite
        return sqlite3.connect("nexa_local.db")


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    if CLOUD_DB and 'postgresql' in str(conn):
        print("✓ Inicjalizacja bazy PostgreSQL...")


        cur.execute("""
                    SELECT EXISTS (SELECT
                    FROM information_schema.tables
                    WHERE table_name = 'users');
                    """)

        table_exists = cur.fetchone()[0]

        if not table_exists:
            print("✓ Tworzę tabelę users...")
            cur.execute("""
                        CREATE TABLE users
                        (
                            id                 SERIAL PRIMARY KEY,
                            username           VARCHAR(50) UNIQUE  NOT NULL,
                            email              VARCHAR(100) UNIQUE NOT NULL,
                            password           VARCHAR(100)        NOT NULL,
                            reset_code         VARCHAR(10),
                            reset_code_expires BIGINT,
                            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """)
            print("✓ Tabela users utworzona!")
        else:
            print("✓ Tabela users już istnieje")

        # Sprawdź czy kolumna reset_code_expires istnieje
        try:
            cur.execute("""
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_name = 'users'
                        AND column_name = 'reset_code_expires';
                        """)
            if not cur.fetchone():
                cur.execute("ALTER TABLE users ADD COLUMN reset_code_expires BIGINT;")
                print("✓ Dodano kolumnę reset_code_expires")
        except Exception as e:
            print(f"ℹ Kolumna reset_code_expires już istnieje: {e}")

    else:
        #SQLite - lokalnie
        print("ℹ Inicjalizacja bazy SQLite lokalnie...")
        cur.execute("""
                CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                reset_code VARCHAR(10),
                reset_code_expires BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
                    """)

    conn.commit()
    conn.close()
    print("✓ Baza danych gotowa!")


#inicalizacja przy imporcie
if __name__ != "__main__":
    init_db()
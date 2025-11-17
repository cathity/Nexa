
import os
from datebase import init_db

print("Inicjalizacja bazy danych na Railway...")

if os.environ.get('RAILWAY_ENVIRONMENT'):
    print("✓ Środowisko Railway wykryte")

    init_db()

    print("Baza danych gotowa!")
    print("Aplikacja Nexa używa teraz wspólnej bazy PostgreSQL")
    print("Uruchom aplikację lokalnie: python PythonApplication2.py")

    # Utrzymuj kontener przy życiu
    try:
        while True:
            # Kontener będzie działał i serwował bazę
            pass
    except KeyboardInterrupt:
        print("Zatrzymywanie...")
else:
    print("To nie jest środowisko Railway")
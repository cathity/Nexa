from database import get_connection
from email_utils import send_reset_code, send_verification_email
import random
import string
import time


def validate_registration(username, email, password1, password2):
    if len(username) < 5:
        return False, "Login musi miec co najmniej 5 znaków."

    if "@" not in email or "." not in email:
        return False, "Adres email jest niepoprawny."

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if cur.fetchone():
        conn.close()
        return False, "Email jest juz uzywany."
    conn.close()

    if password1 != password2:
        return False, "Hasla nie sa takie same."

    if len(password1) < 6:
        return False, "Haslo musi mieć co najmniej 6 znakow."

    return True, None

def generate_verification_code():
    return "".join(random.choices(string.digits, k=6))

def register_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        if cur.fetchone():
            return False, "Nazwa użytkownika jest juz zajeta."

        # czy email istnieje
        cur.execute("SELECT id FROM users WHERE email=?", (email,))
        if cur.fetchone():
            return False, "Email jest już używany."

        verification_code = generate_verification_code()
        expires_at = int(time.time()) + 86400  # 24 godziny

        cur.execute("""INSERT INTO users (username, email, password, email_verification_code, verification_code_expires) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (username, email, password, verification_code, expires_at))
        conn.commit()

        # email weryfikacyjny
        if send_verification_email(email, verification_code):
            return True, "Rejestracja udana! Sprawdź email i wprowadź kod weryfikacyjny."
        else:
            return False, "Rejestracja nieudana. Nie udało się wysłać emaila weryfikacyjnego. Spróbuj ponownie."

    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def verify_email_code(email, code):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT email_verification_code, verification_code_expires FROM users WHERE email=?", (email,))
        result = cur.fetchone()

        if not result:
            return False, "Email nie istnieje."

        stored_code, expires_at = result

        #wygaszenie kodu
        if expires_at and int(time.time()) > expires_at:
            return False, "Kod weryfikacyjny wygasł. Wyślij nowy."

        if stored_code != code:
            return False, "Niepoprawny kod weryfikacyjny."

        #aktywacja konta
        cur.execute(
            "UPDATE users SET email_verified=1, email_verification_code=NULL, verification_code_expires=NULL WHERE email=?",
            (email,))
        conn.commit()

        return True, "Email został pomyślnie zweryfikowany! Możesz się teraz zalogować."

    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def resend_verification_code(email):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT id, email_verified FROM users WHERE email=?", (email,))
        result = cur.fetchone()

        if not result:
            return False, "Email nie istnieje."

        user_id, email_verified = result

        if email_verified:
            return False, "Email jest już zweryfikowany."

        new_code = generate_verification_code()
        expires_at = int(time.time()) + 86400  # 24 godziny

        cur.execute("UPDATE users SET email_verification_code=?, verification_code_expires=? WHERE email=?",
                    (new_code, expires_at, email))
        conn.commit()

        if send_verification_email(email, new_code):
            return True, "Nowy kod weryfikacyjny został wysłany na Twój email."
        else:
            return False, "Błąd podczas wysyłania kodu weryfikacyjnego."

    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, username, email_verified FROM users WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()

    conn.close()

    if user:

        user_id, username, email_verified = user
        return {"id": user_id, "username": username, "verified": bool(email_verified)}
        return None

def generate_reset_code():
    return "".join(random.choices(string.digits, k=6))


def set_reset_code(email):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email=?", (email,))
    if not cur.fetchone():
        conn.close()
        return False, "Email nie istnieje w naszej bazie danych."

    code = generate_reset_code()

    # timestamp wygaśnięcia kodu
    expires_at = int(time.time()) + 3600

    cur.execute("UPDATE users SET reset_code=?, reset_code_expires=? WHERE email=?",
                (code, expires_at, email))
    conn.commit()
    conn.close()

    # email z kodem
    if send_reset_code(email, code):
        return True, "Kod resetujący został wysłany na podany adres email."
    else:
        return False, "Błąd podczas wysyłania kodu resetującego. Spróbuj ponownie później."


def reset_password(email, code, new_password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT reset_code, reset_code_expires FROM users WHERE email=?", (email,))
    row = cur.fetchone()

    if not row:
        conn.close()
        return False, "Email nie istnieje."

    stored_code, expires_at = row

    # sprawdzenie czy kod wygasł
    if expires_at and int(time.time()) > expires_at:
        conn.close()
        return False, "Kod resetujący wygasł. Wygeneruj nowy kod."

    if stored_code != code:
        conn.close()
        return False, "Kod resetu niepoprawny."

    if len(new_password) < 6:
        conn.close()
        return False, "Hasło musi mieć co najmniej 6 znaków."

    cur.execute("UPDATE users SET password=?, reset_code=NULL, reset_code_expires=NULL WHERE email=?",
                (new_password, email))
    conn.commit()
    conn.close()

    return True, "Hasło zostało pomyślnie zmienione!"
import hashlib
import random
import string
import time
from supabase_client import get_supabase


def hash_password(password: str) -> str:
    """Hashowanie hasła"""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_registration(username, email, password1, password2):
    """Walidacja danych rejestracji"""
    if len(username) < 5:
        return False, "Login musi mieć co najmniej 5 znaków."

    if "@" not in email or "." not in email:
        return False, "Adres email jest niepoprawny."

    # Sprawdź czy email już istnieje
    supabase = get_supabase()
    if supabase:
        try:
            result = supabase.table("users") \
                .select("email") \
                .eq("email", email) \
                .execute()

            if result.data and len(result.data) > 0:
                return False, "Email jest już używany."
        except Exception as e:
            print(f"Błąd sprawdzania emaila: {e}")

    if password1 != password2:
        return False, "Hasła nie są takie same."

    if len(password1) < 6:
        return False, "Hasło musi mieć co najmniej 6 znaków."

    return True, None


def generate_verification_code():
    """Generuje 6-cyfrowy kod weryfikacyjny"""
    return "".join(random.choices(string.digits, k=6))


def register_user(username, email, password):
    """Rejestracja użytkownika"""
    try:
        supabase = get_supabase()
        if not supabase:
            return False, "Błąd połączenia z bazą danych."

        # Hashowanie hasła
        password_hash = hash_password(password)

        # Generowanie kodu weryfikacyjnego
        verification_code = generate_verification_code()
        expires_at = int(time.time()) + 86400  # 24 godziny

        # Wstawianie użytkownika do bazy
        result = supabase.table("users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "email_verification_code": verification_code,
            "verification_code_expires": expires_at,
            "email_verified": False
        }).execute()

        if result.data and len(result.data) > 0:
            from email_utils import send_verification_email

            if send_verification_email(email, verification_code):
                return True, "Rejestracja udana! Sprawdź email i wprowadź kod weryfikacyjny."
            else:
                return True, "Rejestracja udana, ale nie udało się wysłać emaila."

        return False, "Błąd podczas rejestracji użytkownika."

    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            if "username" in error_msg:
                return False, "Nazwa użytkownika jest już zajęta."
            elif "email" in error_msg:
                return False, "Email jest już używany."
        return False, f"Błąd rejestracji: {error_msg}"


def verify_email_code(email, code):
    """Weryfikacja kodu email"""
    try:
        supabase = get_supabase()
        if not supabase:
            return False, "Błąd połączenia z bazą danych."

        # Pobierz użytkownika
        result = supabase.table("users") \
            .select("email_verification_code, verification_code_expires, email_verified") \
            .eq("email", email) \
            .execute()

        if not result.data or len(result.data) == 0:
            return False, "Email nie istnieje."

        user_data = result.data[0]
        stored_code = user_data.get("email_verification_code")
        expires_at = user_data.get("verification_code_expires")

        if user_data.get("email_verified"):
            return True, "Email jest już zweryfikowany."

        if expires_at and int(time.time()) > expires_at:
            return False, "Kod weryfikacyjny wygasł. Wyślij nowy."

        if stored_code != code:
            return False, "Niepoprawny kod weryfikacyjny."

        # Aktualizuj jako zweryfikowany
        update_result = supabase.table("users") \
            .update({
            "email_verified": True,
            "email_verification_code": None,
            "verification_code_expires": None
        }) \
            .eq("email", email) \
            .execute()

        return True, "Email został pomyślnie zweryfikowany!"

    except Exception as e:
        return False, f"Błąd weryfikacji: {str(e)}"


def resend_verification_code(email):
    """Ponowne wysłanie kodu weryfikacyjnego"""
    try:
        supabase = get_supabase()
        if not supabase:
            return False, "Błąd połączenia z bazą danych."

        result = supabase.table("users") \
            .select("id, email_verified") \
            .eq("email", email) \
            .execute()

        if not result.data or len(result.data) == 0:
            return False, "Email nie istnieje."

        user_data = result.data[0]

        if user_data.get("email_verified"):
            return False, "Email jest już zweryfikowany."

        new_code = generate_verification_code()
        expires_at = int(time.time()) + 86400

        update_result = supabase.table("users") \
            .update({
            "email_verification_code": new_code,
            "verification_code_expires": expires_at
        }) \
            .eq("email", email) \
            .execute()

        from email_utils import send_verification_email
        if send_verification_email(email, new_code):
            return True, "Nowy kod weryfikacyjny został wysłany."
        else:
            return False, "Błąd podczas wysyłania kodu."

    except Exception as e:
        return False, f"Błąd: {str(e)}"


def login_user(username, password):
    """Logowanie użytkownika"""
    try:
        supabase = get_supabase()
        if not supabase:
            return None

        password_hash = hash_password(password)

        result = supabase.table("users") \
            .select("id, username, email, email_verified") \
            .or_(f"username.eq.{username},email.eq.{username}") \
            .eq("password_hash", password_hash) \
            .execute()

        if result.data and len(result.data) > 0:
            user = result.data[0]

            user_id = str(user["id"])

            return {
                "id": user_id,
                "username": user["username"],
                "email": user["email"],
                "verified": bool(user["email_verified"])
            }

        return None

    except Exception as e:
        print(f"Błąd logowania: {e}")
        return None

def generate_reset_code():
    """Generuje 6-cyfrowy kod resetujący"""
    return "".join(random.choices(string.digits, k=6))


def set_reset_code(email):
    """Ustawia kod resetujący hasło"""
    try:
        supabase = get_supabase()
        if not supabase:
            return False, "Błąd połączenia z bazą danych."

        result = supabase.table("users") \
            .select("id") \
            .eq("email", email) \
            .execute()

        if not result.data or len(result.data) == 0:
            return False, "Email nie istnieje."

        user_id = result.data[0]["id"]

        code = generate_reset_code()
        expires_at = int(time.time()) + 3600

        update_result = supabase.table("users") \
            .update({
            "reset_code": code,
            "reset_code_expires": expires_at
        }) \
            .eq("id", user_id) \
            .execute()

        from email_utils import send_reset_code
        if send_reset_code(email, code):
            return True, "Kod resetujący został wysłany."
        else:
            return False, "Błąd podczas wysyłania kodu."

    except Exception as e:
        return False, f"Błąd: {str(e)}"


def reset_password(email, code, new_password):
    """Resetowanie hasła z użyciem kodu"""
    try:
        supabase = get_supabase()
        if not supabase:
            return False, "Błąd połączenia z bazą danych."

        result = supabase.table("users") \
            .select("id, reset_code, reset_code_expires") \
            .eq("email", email) \
            .execute()

        if not result.data or len(result.data) == 0:
            return False, "Email nie istnieje."

        user_data = result.data[0]
        stored_code = user_data.get("reset_code")
        expires_at = user_data.get("reset_code_expires")

        if expires_at and int(time.time()) > expires_at:
            return False, "Kod resetujący wygasł."

        if stored_code != code:
            return False, "Kod resetu niepoprawny."

        if len(new_password) < 6:
            return False, "Hasło musi mieć co najmniej 6 znaków."

        new_password_hash = hash_password(new_password)

        update_result = supabase.table("users") \
            .update({
            "password_hash": new_password_hash,
            "reset_code": None,
            "reset_code_expires": None
        }) \
            .eq("email", email) \
            .eq("reset_code", code) \
            .execute()

        if update_result.data:
            return True, "Hasło zostało pomyślnie zmienione!"
        else:
            return False, "Nie udało się zmienić hasła."

    except Exception as e:
        return False, f"Błąd resetowania hasła: {str(e)}"

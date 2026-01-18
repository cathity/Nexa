from supabase_client import get_supabase

def get_shared_with_me(current_user_id, friend_id):
    """Pobiera notatki, które przyjaciel udostępnił MI"""
    supabase = get_supabase()
    if not supabase: return []

    try:
        # Pobieramy wpisy z shared_notes, gdzie:
        # 1. shared_with_id to JA (current_user_id)
        # 2. Notatka należy do PRZYJACIELA (filtrowanie po relacji notes)
        
        response = supabase.table("shared_notes") \
            .select("id, note_id, notes!inner(title, content, user_id)") \
            .eq("shared_with_id", current_user_id) \
            .eq("notes.user_id", friend_id) \
            .execute()
            
        notes = []
        for item in response.data:
            note_data = item.get('notes')
            if note_data:
                notes.append({
                    "share_id": item['id'],      # ID udostępnienia
                    "title": note_data['title'],
                    "content": note_data['content']
                })
        return notes
    except Exception as e:
        print(f"Błąd get_shared_with_me: {e}")
        return []

def get_shared_by_me(current_user_id, friend_id):
    """Pobiera notatki, które JA udostępniłem przyjacielowi"""
    supabase = get_supabase()
    if not supabase: return []

    try:
        # Pobieramy wpisy, gdzie:
        # 1. shared_with_id to PRZYJACIEL
        # 2. Notatka należy do MNIE
        
        response = supabase.table("shared_notes") \
            .select("id, note_id, notes!inner(title, user_id)") \
            .eq("shared_with_id", friend_id) \
            .eq("notes.user_id", current_user_id) \
            .execute()

        notes = []
        for item in response.data:
            note_data = item.get('notes')
            if note_data:
                notes.append({
                    "share_id": item['id'],
                    "title": note_data['title']
                })
        return notes
    except Exception as e:
        print(f"Błąd get_shared_by_me: {e}")
        return []

def get_my_notes_to_share(current_user_id):
    """Pobiera listę moich notatek (do wyboru przy udostępnianiu)"""
    supabase = get_supabase()
    if not supabase: return []
    
    try:
        response = supabase.table("notes") \
            .select("id, title") \
            .eq("user_id", current_user_id) \
            .execute()
        return response.data or []
    except Exception as e:
        return []

def share_note(note_id, friend_id):
    """Udostępnia notatkę znajomemu"""
    supabase = get_supabase()
    try:
        supabase.table("shared_notes").insert({
            "note_id": note_id,
            "shared_with_id": friend_id
        }).execute()
        return True, "Notatka udostępniona!"
    except Exception as e:
        if "duplicate" in str(e):
            return False, "Ta notatka jest już udostępniona tej osobie."
        return False, str(e)

def revoke_access(share_id):
    """Zabiera dostęp do notatki"""
    supabase = get_supabase()
    try:
        supabase.table("shared_notes").delete().eq("id", share_id).execute()
        return True, "Dostęp usunięty."
    except Exception as e:
        return False, str(e)

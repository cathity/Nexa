from supabase_client import get_supabase

def send_friend_request(current_user_id, target_username):
    """Wysyła zaproszenie do znajomych na podstawie nazwy użytkownika"""
    supabase = get_supabase()
    if not supabase:
        return False, "Brak połączenia z bazą."

    try:
        # 1. Znajdź ID użytkownika po nazwie (username)
        response = supabase.table("users").select("id, username").eq("username", target_username).execute()
        
        if not response.data:
            return False, "Nie znaleziono użytkownika o takiej nazwie."
            
        target_user = response.data[0]
        target_id = target_user['id']

        # Zabezpieczenie przed dodaniem samego siebie
        if str(target_id) == str(current_user_id):
            return False, "Nie możesz wysłać zaproszenia do siebie."

        # 2. Sprawdź, czy relacja już istnieje (w obie strony)
        # Sprawdzamy czy my wysłaliśmy, LUB czy on wysłał do nas
        existing = supabase.table("friends").select("*").or_(
            f"and(requester_id.eq.{current_user_id},receiver_id.eq.{target_id}),"
            f"and(requester_id.eq.{target_id},receiver_id.eq.{current_user_id})"
        ).execute()

        if existing.data:
            return False, "Zaproszenie już istnieje lub jesteście już znajomymi."

        # 3. Wyślij zaproszenie (status 'pending')
        insert_data = {
            "requester_id": current_user_id,
            "receiver_id": target_id,
            "status": "pending"
        }
        
        supabase.table("friends").insert(insert_data).execute()
        return True, f"Wysłano zaproszenie do {target_username}!"

    except Exception as e:
        return False, f"Błąd: {str(e)}"

def get_incoming_requests(current_user_id):
    """Pobiera listę oczekujących zaproszeń (gdzie my jesteśmy odbiorcą)"""
    supabase = get_supabase()
    if not supabase:
        return []

    try:
        # Pobierz wiersze, gdzie receiver_id to MY i status to 'pending'
        # Pobieramy też dane osoby, która wysłała (users:requester_id)
        response = supabase.table("friends") \
            .select("id, requester_id, users:requester_id(username, email)") \
            .eq("receiver_id", current_user_id) \
            .eq("status", "pending") \
            .execute()
            
        requests_list = []
        for item in response.data:
            requester_info = item.get('users')
            if requester_info:
                requests_list.append({
                    "request_id": item['id'], # ID rekordu w tabeli friends
                    "username": requester_info['username']
                })
        return requests_list
    except Exception as e:
        print(f"Błąd pobierania zaproszeń: {e}")
        return []

def accept_friend_request(request_id):
    """Akceptuje zaproszenie (zmienia status na 'accepted')"""
    supabase = get_supabase()
    if not supabase:
        return False, "Brak bazy"

    try:
        supabase.table("friends").update({"status": "accepted"}).eq("id", request_id).execute()
        return True, "Zaakceptowano zaproszenie!"
    except Exception as e:
        return False, str(e)

def reject_friend_request(request_id):
    """Odrzuca zaproszenie (usuwa wiersz)"""
    supabase = get_supabase()
    if not supabase:
        return False, "Brak bazy"
        
    try:
        supabase.table("friends").delete().eq("id", request_id).execute()
        return True, "Odrzucono zaproszenie."
    except Exception as e:
        return False, str(e)

def get_user_friends(current_user_id):
    """Pobiera listę zaakceptowanych znajomych"""
    supabase = get_supabase()
    if not supabase:
        return []

    try:
        # POPRAWKA: Dodano 'id' do listy pobieranych pól w nawiasach
        
        # 1. Pobierz gdzie ja byłem requesterem
        sent = supabase.table("friends") \
            .select("receiver_id, users:receiver_id(id, username, email)") \
            .eq("requester_id", current_user_id) \
            .eq("status", "accepted") \
            .execute()

        # 2. Pobierz gdzie ja byłem receiverem
        received = supabase.table("friends") \
            .select("requester_id, users:requester_id(id, username, email)") \
            .eq("receiver_id", current_user_id) \
            .eq("status", "accepted") \
            .execute()
        
        friends_list = []
        
        # Przetwórz te, które ja wysłałem
        for item in sent.data:
            friend_info = item.get('users')
            if friend_info:
                friends_list.append(friend_info)

        # Przetwórz te, które otrzymałem
        for item in received.data:
            friend_info = item.get('users')
            if friend_info:
                friends_list.append(friend_info)

        return friends_list

    except Exception as e:
        print(f"Błąd pobierania znajomych: {e}")
        return []

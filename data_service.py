from supabase_client import supabase

class DataService:

    def login(self, email, password):
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response.user

    def register(self, email, password):
        supabase.auth.sign_up({
            "email": email,
            "password": password
        })

    def get_notes(self, user_id):
        res = supabase.table("notes") \
            .select("*") \
            .eq("user_id", user_id) \
            .execute()
        return res.data

    def add_note(self, user_id, title, content):
        supabase.table("notes").insert({
            "user_id": user_id,
            "title": title,
            "content": content
        }).execute()

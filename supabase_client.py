from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://rtmcakhlhzykaaxztnfj.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_lwJoiykWX4q2cJk9U4R48A_gABldDbN")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f" Błąd połączenia z Supabase: {e}")
    supabase = None

def get_supabase():
    return supabase

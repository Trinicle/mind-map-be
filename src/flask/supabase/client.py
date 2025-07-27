from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()


def get_client() -> Client:
    """
    Returns a singleton instance of the Supabase client.
    The client automatically handles authentication context including the user's session.
    """
    if not hasattr(get_client, "_instance"):
        get_client._instance = create_client(
            os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY")
        )
    return get_client._instance


supabase = get_client()

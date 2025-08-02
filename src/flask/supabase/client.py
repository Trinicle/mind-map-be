from supabase import ClientOptions, create_client as create_supabase_client, Client
import os
from dotenv import load_dotenv
from flask import Request

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def get_client(request: Request = None) -> Client:
    """
    Create a Supabase client for the current request.
    If request is provided and has Authorization header, creates an authenticated client.
    Otherwise returns an anonymous client.
    """
    options = None
    if request and request.headers.get("Authorization"):
        auth_token = request.headers["Authorization"].replace("Bearer ", "")
        options = ClientOptions(headers={"Authorization": f"Bearer {auth_token}"})

    return create_supabase_client(SUPABASE_URL, SUPABASE_KEY, options)


def get_client_from_auth_token(auth_token: str) -> Client:
    """
    Create a Supabase client for the current request.
    If request is provided and has Authorization header, creates an authenticated client.
    Otherwise returns an anonymous client.
    """
    options = ClientOptions(headers={"Authorization": f"Bearer {auth_token}"})
    return create_supabase_client(SUPABASE_URL, SUPABASE_KEY, options)

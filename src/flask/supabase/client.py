from supabase import AsyncClient, ClientOptions, create_client, acreate_client, Client
import os
from dotenv import load_dotenv
from flask import Request


def get_supabase_config():
    """Get Supabase configuration, ensuring .env is loaded fresh each time."""
    load_dotenv()  # Reload environment variables
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            f"Missing Supabase configuration: URL={url}, KEY={'***' if key else 'None'}"
        )

    return url, key


def get_client(request: Request = None) -> Client:
    """
    Create a Supabase client for the current request.
    If request is provided and has Authorization header, creates an authenticated client.
    Otherwise returns an anonymous client.
    """
    url, key = get_supabase_config()

    options = None
    if request and request.headers.get("Authorization"):
        auth_token = request.headers["Authorization"].replace("Bearer ", "")
        options = ClientOptions(headers={"Authorization": f"Bearer {auth_token}"})

    return create_client(url, key, options)


def get_async_client(request: Request = None) -> AsyncClient:
    """
    Create an async Supabase client for the current request.
    """
    url, key = get_supabase_config()

    options = None
    if request and request.headers.get("Authorization"):
        auth_token = request.headers["Authorization"].replace("Bearer ", "")
        options = ClientOptions(headers={"Authorization": f"Bearer {auth_token}"})

    return acreate_client(url, key, options)


def get_client_from_auth_token(auth_token: str) -> Client:
    """
    Create a Supabase client for the current request.
    If request is provided and has Authorization header, creates an authenticated client.
    Otherwise returns an anonymous client.
    """
    url, key = get_supabase_config()

    # Ensure token has Bearer prefix, but don't double-add it
    if not auth_token.startswith("Bearer "):
        auth_token = f"Bearer {auth_token}"

    options = ClientOptions(headers={"Authorization": auth_token})
    return create_client(url, key, options)


def get_async_client_from_auth_token(auth_token: str) -> AsyncClient:
    """
    Create an async Supabase client for the current request.
    """
    url, key = get_supabase_config()

    # Ensure token has Bearer prefix, but don't double-add it
    if not auth_token.startswith("Bearer "):
        auth_token = f"Bearer {auth_token}"

    options = ClientOptions(headers={"Authorization": auth_token})
    return acreate_client(url, key, options)


def get_auth_token(request: Request) -> str:
    """
    Get the auth token from the request.
    """
    return request.headers["Authorization"].replace("Bearer ", "")

from supabase import ClientOptions, create_client, Client
import os
from dotenv import load_dotenv
import httpx
from supabase.lib.client_options import DEFAULT_HEADERS

load_dotenv()


def get_client() -> Client:
    client = httpx.Client(
        timeout=30.0,
        limits=httpx.Limits(max_connections=20),
        transport=httpx.HTTPTransport(retries=3),
    )

    options = ClientOptions(
        headers=DEFAULT_HEADERS, httpx_client=client, postgrest_client_timeout=30
    )
    return create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"), options)


supabase = get_client()

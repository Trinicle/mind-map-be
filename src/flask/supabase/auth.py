from typing import TypedDict, NotRequired
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from gotrue.types import AuthResponse

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))


class UserModel(TypedDict):
    email: str
    password: str
    firstName: NotRequired[str | None]
    lastName: NotRequired[str | None]


def signup(user: UserModel) -> AuthResponse:
    metadata = {}
    if "firstName" in user and user["firstName"] is not None:
        metadata["firstName"] = user["firstName"]
    if "lastName" in user and user["lastName"] is not None:
        metadata["lastName"] = user["lastName"]

    return supabase.auth.sign_up(
        {
            "email": user["email"],
            "password": user["password"],
            "options": {"data": metadata},
        }
    )


def login(email: str, password: str) -> AuthResponse:
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

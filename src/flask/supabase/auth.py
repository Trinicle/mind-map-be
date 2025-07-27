from typing import TypedDict, NotRequired
from gotrue.types import AuthResponse
from .client import supabase


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


def signin(email: str, password: str) -> AuthResponse:
    return supabase.auth.sign_in_with_password({"email": email, "password": password})


def signout():
    return supabase.auth.sign_out()


def get_session():
    return supabase.auth.get_session()


def get_user():
    """Get the current authenticated user"""
    session = get_session()
    return session.user if session else None

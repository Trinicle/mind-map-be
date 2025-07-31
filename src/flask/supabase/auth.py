from typing import TypedDict, NotRequired
from gotrue.types import AuthResponse
from flask import Request
from .client import get_client


class UserModel(TypedDict):
    email: str
    password: str
    firstName: NotRequired[str | None]
    lastName: NotRequired[str | None]


def signup(user: UserModel) -> AuthResponse:
    """Sign up a new user"""
    client = get_client()
    metadata = {}
    if "firstName" in user and user["firstName"] is not None:
        metadata["firstName"] = user["firstName"]
    if "lastName" in user and user["lastName"] is not None:
        metadata["lastName"] = user["lastName"]

    return client.auth.sign_up(
        {
            "email": user["email"],
            "password": user["password"],
            "options": {"data": metadata},
        }
    )


def signin(email: str, password: str) -> AuthResponse:
    """Sign in an existing user"""
    client = get_client()
    return client.auth.sign_in_with_password({"email": email, "password": password})


def signout(request: Request):
    """Sign out the current user"""
    client = get_client(request)
    return client.auth.sign_out()


def get_session(request: Request):
    """Get the current session from the request"""
    client = get_client(request)
    return client.auth.get_session()


def get_user(request: Request):
    """Get the current authenticated user from the request"""
    session = get_session(request)
    return session.user if session else None

"""Module with user's validation schemes."""

from typing import List

from pydantic import BaseModel


class UserOutShort(BaseModel):
    """Base scheme of "User" model realization."""

    name: str


class UserOutShortAuthor(UserOutShort):
    """GET-request output scheme of "User" model realization. Short version. Author."""

    id: int

    class Config:
        orm_mode = True


class UserOutShortLike(UserOutShort):
    """GET-request output scheme of User model realization. Short version. Liked user."""

    user_id: int


class UserOutFull(UserOutShortAuthor):
    """GET-request output scheme of "User" model realization. Full version."""

    followers: List['UserOutShortAuthor']
    following: List['UserOutShortAuthor']

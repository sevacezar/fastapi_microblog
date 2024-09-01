"""Module with tweet's validation schemes."""

from typing import List, Optional

from pydantic import BaseModel

from users.schemas import UserOutShortAuthor, UserOutShortLike


class TweetIn(BaseModel):
    """POST-request input scheme of "Tweet" model realization."""

    tweet_data: str
    tweet_media_ids: Optional[List[int]] = None


class TweetOut(BaseModel):
    """GET-request output scheme of "Tweet" model realization."""

    id: int
    content: str
    attachments: List[Optional[str]]
    author: UserOutShortAuthor
    likes: List[Optional[UserOutShortLike]]

    class Config:
        orm_mode = True

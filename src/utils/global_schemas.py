"""Module with common validation schemes."""

from typing import List

from pydantic import BaseModel

from tweets.schemas import TweetOut
from users.schemas import UserOutFull


class BaseResponse(BaseModel):
    """Base scheme of response."""

    result: bool


class ResponseTweetPost(BaseResponse):
    """Output scheme of response while posting new tweet."""

    tweet_id: int

    class Config:
        orm_mode = True


class ResponseMediaPost(BaseResponse):
    """Output scheme of response while posting new media."""

    media_id: int

    class Config:
        orm_mode = True


class ResponseTweetsGet(BaseResponse):
    """Output scheme of response while getting tweets of user's feed."""

    tweets: List[TweetOut]


class ResponseError(BaseResponse):
    """Output scheme of response while getting error."""

    error_type: str
    error_message: str


class ResponseUserGet(BaseResponse):
    """Output scheme of response while getting user's info."""

    user: 'UserOutFull'

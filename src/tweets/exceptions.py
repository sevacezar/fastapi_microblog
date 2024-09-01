
"""Module with custom exceptions on tweet's router."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from exceptions import BaseError


class TweetNotFoundError(BaseError):
    """Exceptions when it's not possible to find tweet by id."""

    pass


async def tweet_exception_handler(request: Request, exc: TweetNotFoundError):
    """TweetNotFoundError handler."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.content,
    )


class NonUserTweetError(BaseError):
    """Exceptions when it's invalid operation with tweet."""

    pass


async def non_user_tweet_exception_handler(request: Request, exc: NonUserTweetError):
    """NonUserTweetError handler."""
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=exc.content,
    )

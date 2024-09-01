"""Module with custom exceptions on user's router."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from exceptions import BaseError


class UserNotFoundError(BaseError):
    """Exceptions when it's not possible to find user by id or api-key."""

    pass


async def user_exception_handler(request: Request, exc: UserNotFoundError):
    """UserNotFoundError handler."""

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=exc.content,
    )

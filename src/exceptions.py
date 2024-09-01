"""Module with common custom exceptions and handlers."""

from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class BaseError(Exception):
    """Base class of common custom exceptions."""

    def __init__(self, message: str):
        self.content: dict[str, Union[bool, str]] = {
            'result': False,
            'error_type': self.__class__.__name__,
            'error_message': message,
        }


class RelationshipError(BaseError):
    """Exception class repeated following, unfollowing, liking, unliking."""

    pass


async def relationship_exception_handler(request: Request, exc: RelationshipError):
    """Relationship exception handler."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.content,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Validation error hadler."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'result': False,
            'error_type': 'ValidationError',
            'error_message': str(exc.errors()[0]),
            },
    )

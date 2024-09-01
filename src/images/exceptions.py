"""Module with custom exceptions on files uploading router."""

from fastapi import Request, status
from fastapi.responses import JSONResponse

from exceptions import BaseError


class FileSizeError(BaseError):
    """Exceptions when file size is too large."""

    pass


class FileTypeError(BaseError):
    """Exceptions when file type is invalid."""

    pass


class FileMalwareError(BaseError):
    """Exceptions when file consist malware."""

    pass


async def file_size_exception_handler(request: Request, exc: FileSizeError):
    """FileSizeError handler."""
    return JSONResponse(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        content=exc.content,
    )


async def file_type_exception_handler(request: Request, exc: FileTypeError):
    """FileTypeError handler."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.content,
    )


async def file_malware_exception_handler(request: Request, exc: FileMalwareError):
    """FileMalwareError handler."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=exc.content,
    )

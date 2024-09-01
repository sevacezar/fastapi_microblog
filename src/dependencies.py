"""Module with dependencies of FastAPI app."""


from typing import Optional

from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import async_session
from users.exceptions import UserNotFoundError
from users.models import User
from users.service import get_user_by_api_key


async def get_session() -> AsyncSession:
    """Function of async sessions getting."""
    async with async_session() as session:
        yield session


async def get_user_by_api_key_dependencie(
        api_key: str = Header(None),
        session: AsyncSession = Depends(get_session)):
    """Function of getting user by api-key."""
    if not api_key:
        raise UserNotFoundError(message='Passed api-key is empty')

    user: Optional[User] = await get_user_by_api_key(session=session, api_key=api_key)
    if not user:
        raise UserNotFoundError(message='User with the passed api-key is not exist')

    return user

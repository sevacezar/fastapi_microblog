"""Module with DB-operations with users."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from utils.keys_generator import generate_key
from users.models import User


async def get_user_by_api_key(session: AsyncSession, api_key: str) -> Optional[User]:
    """Function of getting user by api-key."""
    user = await User.get_user_by_api_key(session=session, api_key=api_key)

    return user


async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
    """Function of getting user by id."""
    user = await User.get_user_by_id(session=session, user_id=user_id)

    return user


async def create_user(session: AsyncSession, name: str, api_key_len: int) -> User:
    """Function of creating user with name."""
    users = await session.execute(select(User))
    users = users.scalars().all()

    if users:
        api_key = generate_key(length=api_key_len)
    else:
        api_key = 'test'

    user = User(name=name, api_key=api_key)
    session.add(user)
    await session.commit()

    return user

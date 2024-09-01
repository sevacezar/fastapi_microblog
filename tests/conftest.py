"""Module with common app tests."""

import os
import sys

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from database import Base
from dependencies import get_session
from main import app_api
from users.models import User

DATABASE_URL_TESTS = 'postgresql+asyncpg://postgres:postgres@localhost:5433/test'

# poolclass=NullPool - is necessary!
engine = create_async_engine(url=DATABASE_URL_TESTS, poolclass=NullPool)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_session() -> AsyncSession:
    """Function of async DB-sessions generation."""
    async with async_session() as session:
        yield session


app_api.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope='function', autouse=True)
async def setup_database():
    """Function of database setup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def client() -> AsyncClient:
    """Function of async pytest client generation."""
    async with AsyncClient(app=app_api, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='function')
async def db() -> AsyncSession:
    """Function of async DB-session generation."""
    async with async_session() as session:
        yield session


@pytest.fixture(scope='function')
async def test_user_1(db: AsyncSession):
    """Function of getting test user # 1."""
    user = User(name='Rihanna', api_key='umbrella')
    db.add(user)
    await db.commit()
    return user


@pytest.fixture(scope='function')
async def test_user_2(db: AsyncSession):
    """Function of getting test user # 2."""
    user = User(name='Rocky', api_key='asap')
    db.add(user)
    await db.commit()
    return user

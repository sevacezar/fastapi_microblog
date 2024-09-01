"""Module with DB users' models."""

from typing import Dict, Optional

from sqlalchemy import Column, String, Integer, ForeignKey, Table
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, backref, selectinload

from database import Base
from likes.models import likes
from utils.keys_generator import generate_key

API_KEY_SIZE: int = 16

# Table with followers
followers = Table(
    'followers',
    Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id')),
    Column('followed_id', Integer, ForeignKey('users.id')),
)


class User(Base):
    """DB user's model."""

    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    api_key = Column(String, nullable=False, unique=True)
    followed = relationship(
        'User',
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=backref('followers', lazy='selectin'),
        lazy='selectin',
    )

    tweets = relationship('Tweet', back_populates='user')
    liked_tweets = relationship('Tweet', secondary=likes, back_populates='liked_users')

    def to_json(self) -> Dict[str, str]:
        """Function of convertation objs to JSON."""
        return {
            'id': self.id,
            'name': self.name,
            'followers': self.followers,
            'following': self.followed,
        }

    def __repr__(self):
        return f'<User {self.name} with api-key {self.api_key}>'

    @classmethod
    async def get_user_by_id(
        cls,
        session: AsyncSession,
        user_id: str,
    ) -> Optional['User']:
        """Function of getting the user by id."""
        res = await session.execute(select(User).
                                    filter_by(id=user_id).
                                    options(selectinload(User.tweets),
                                            selectinload(User.liked_tweets),
                                            selectinload(User.followed),
                                            selectinload(User.followers)))

        return res.unique().scalars().one_or_none()

    @classmethod
    async def get_user_by_api_key(
        cls,
        session: AsyncSession,
        api_key: str,
    ) -> Optional['User']:
        """Function of getting the user by api-key."""
        res = await session.execute(select(User).
                                    filter_by(api_key=api_key).
                                    options(selectinload(User.tweets),
                                            selectinload(User.liked_tweets),
                                            selectinload(User.followed),
                                            selectinload(User.followers)))

        return res.unique().scalars().one_or_none()

    @classmethod
    async def add_user(cls, session: AsyncSession, name: str) -> 'User':
        """Function of adding new user to DB."""
        all_users = await session.execute(select(User))
        if all_users.unique().scalars().all():
            api_key = generate_key(API_KEY_SIZE)
            user_name = name
        else:
            api_key = 'test'
            user_name = 'test_user'

        new_user = User(name=user_name, api_key=api_key)

        session.add(new_user)
        await session.commit()
        return new_user

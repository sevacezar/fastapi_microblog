"""Module with DB likes' models."""

from sqlalchemy import Column, Integer, ForeignKey, Table

from database import Base


likes = Table(
    'likes',
    Base.metadata,
    Column('tweet_id', Integer, ForeignKey('tweets.id')),
    Column('user_id', Integer, ForeignKey('users.id')),
)

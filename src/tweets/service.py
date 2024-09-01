"""Module with DB-operations with tweets."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from tweets.models import Tweet
from users.models import followers


async def add_tweet_to_db(
        session: AsyncSession,
        content: str,
        user_id: int,
) -> Tweet:
    """Function of adding tweet to DB."""
    tweet_obj: Tweet = Tweet(
        content=content,
        user_id=user_id,
        timestamp=datetime.now(),
    )
    session.add(tweet_obj)
    await session.commit()

    return tweet_obj


async def get_tweet_by_id(
        session: AsyncSession,
        tweet_id: int,
) -> Optional[Tweet]:
    """Function of getting tweet-obj by id."""
    tweet = await Tweet.get_tweet_by_id(session=session, tweet_id=tweet_id)

    return tweet


async def get_tweets_by_following_user(
        session: AsyncSession,
        user_id: int,
) -> List[Optional[Tweet]]:
    """Function of getting all of tweets of followed users."""
    subquery = select(followers.c.followed_id).filter(
        followers.c.follower_id == user_id
    ).subquery()
    tweets_query = await session.execute(select(Tweet).
                                         filter(Tweet.user_id.in_(subquery)).
                                         options(selectinload(Tweet.user),
                                                 selectinload(Tweet.liked_users),
                                                 selectinload(Tweet.attachments)))
    tweets: List[Optional[Tweet]] = tweets_query.scalars().all()

    return tweets


async def get_all_tweets(session: AsyncSession) -> List[Optional[Tweet]]:
    """Function of getting all of tweets."""
    tweets_query = await session.execute(select(Tweet).
                                         order_by(Tweet.timestamp.desc()).
                                         options(selectinload(Tweet.user),
                                                 selectinload(Tweet.liked_users),
                                                 selectinload(Tweet.attachments)))
    tweets: List[Optional[Tweet]] = tweets_query.scalars().all()

    return tweets

"""Module with endpoints of actions with tweets."""

from typing import List, Optional, Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_user_by_api_key_dependencie, get_session
from exceptions import RelationshipError
from images.service import update_medias
from tweets.exceptions import NonUserTweetError, TweetNotFoundError
from tweets.models import Tweet
from tweets.schemas import TweetIn
from tweets.service import add_tweet_to_db, get_tweet_by_id, get_all_tweets
from users.models import User
from utils import global_schemas as sch

router = APIRouter(prefix='/tweets', tags=['Tweets'])


@router.post(
        '',
        response_model=Union[sch.ResponseTweetPost, sch.ResponseError],
)
async def create_tweet(
    tweet: TweetIn,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of POST-request of new tweet creating."""
    # Adding tweet to DB
    tweet_obj = await add_tweet_to_db(
        session=session,
        content=tweet.tweet_data,
        user_id=user.id,
    )

    # Updating tweet_id parameter of medias
    if tweet.tweet_media_ids:
        await update_medias(
            session=session,
            media_ids=tweet.tweet_media_ids,
            new_tweet_id=tweet_obj.id,
        )

    return {'result': True, 'tweet_id': tweet_obj.id}


@router.delete(
        '/{id}',
        response_model=Union[sch.BaseResponse, sch.ResponseError],
)
async def delete_tweet(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of DELETE-request of deleting user's tweet."""
    tweet: Optional[Tweet] = await get_tweet_by_id(session=session, tweet_id=id)

    if not tweet:
        raise TweetNotFoundError(message='Tweet with the passed id is not exist')

    user_tweet_ids = [i_tweet.id for i_tweet in user.tweets]

    if tweet.id in user_tweet_ids:
        await session.delete(tweet)
        await session.commit()
        return {'result': True}

    raise NonUserTweetError(message='Deleting a tweet that does not belong to the user')


@router.post(
        '/{id}/likes',
        response_model=Union[sch.BaseResponse, sch.ResponseError],
)
async def like_tweet(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of POST-request of like some tweet."""
    tweet: Optional[Tweet] = await get_tweet_by_id(session=session, tweet_id=id)
    if not tweet:
        raise TweetNotFoundError(message='Tweet with the passed id is not exist')

    liked_tweets_ids = [i_tweet.id for i_tweet in user.liked_tweets]

    if id not in liked_tweets_ids:
        user.liked_tweets.append(tweet)
        await session.commit()
        return {'result': True}
    else:
        raise RelationshipError(message='The user has already liked this tweet')


@router.delete(
        '/{id}/likes',
        response_model=Union[sch.BaseResponse, sch.ResponseError],
)
async def dislike_tweet(
    id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of DELETE-request of delete user's like."""
    tweet: Optional[Tweet] = await get_tweet_by_id(session=session, tweet_id=id)
    if not tweet:
        raise TweetNotFoundError(message='Tweet with the passed id is not exist')

    liked_tweets_ids = [i_tweet.id for i_tweet in user.liked_tweets]

    if id in liked_tweets_ids:
        user.liked_tweets = [i_tweet for i_tweet in user.liked_tweets if i_tweet.id != id]
        await session.commit()
        return {'result': True}
    else:
        raise RelationshipError(message='There is no like on the tweet')


@router.get(
        '',
        response_model=Union[sch.ResponseTweetsGet, sch.ResponseError],
)
async def get_tweets(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of GET-request of recieving tweets' info."""
    # You should use this part of code instead bellow code to recieve only those tweets,
    # whose users follow
    # tweets: List[Optional[Tweet]] = await get_tweets_by_following_user(session=session,
    #                                                                    user_id=user.id)
    tweets: List[Optional[Tweet]] = await get_all_tweets(session=session)

    tweets_json: List[dict] = [i_tweet.to_json() for i_tweet in tweets]
    return {'result': True, 'tweets': tweets_json}

"""Main module. API launch point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from sqlalchemy import select

import exceptions as common_exc
from database import async_session
from images import exceptions as images_exc
from images.router import router as router_img
from tweets import exceptions as tweet_exc
from tweets.router import router as router_tweet
from users import exceptions as user_exc
from users.models import User
from users.router import router as router_user


# Adding test users when the application starts
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Function-lifespan. Makes actions before app launching."""
    async with async_session() as session:
        res = await session.execute(select(User))
        users = res.scalars().all()

        if not users:
            user1 = User(name='Alex', api_key='test')
            user2 = User(name='Fillipe', api_key='test2')
            session.add_all([user1, user2])
            await session.commit()
        yield


# App initialization
app_api = FastAPI(
    description='This is backend of microblogging service',
    title='Microblogging service API',
    root_path='/api',
    lifespan=lifespan,
)

# Routers connecting
app_api.include_router(router_img)
app_api.include_router(router_tweet)
app_api.include_router(router_user)

# Exception hendlers connecting
app_api.add_exception_handler(
    user_exc.UserNotFoundError, user_exc.user_exception_handler,
)
app_api.add_exception_handler(
    common_exc.RelationshipError, common_exc.relationship_exception_handler,
)
app_api.add_exception_handler(
    RequestValidationError, common_exc.validation_exception_handler,
)
app_api.add_exception_handler(
    tweet_exc.TweetNotFoundError, tweet_exc.tweet_exception_handler,
)
app_api.add_exception_handler(
    tweet_exc.NonUserTweetError, tweet_exc.non_user_tweet_exception_handler,
)
app_api.add_exception_handler(
    images_exc.FileSizeError, images_exc.file_size_exception_handler,
)
app_api.add_exception_handler(
    images_exc.FileTypeError, images_exc.file_type_exception_handler,
)
app_api.add_exception_handler(
    images_exc.FileMalwareError, images_exc.file_malware_exception_handler,
)

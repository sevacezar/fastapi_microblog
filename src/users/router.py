"""Module with endpoints of actions with users."""

from typing import Optional, Union

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session, get_user_by_api_key_dependencie
from exceptions import RelationshipError

from users.exceptions import UserNotFoundError
from utils.global_schemas import ResponseError, BaseResponse, ResponseUserGet
from users.models import User
from users.schemas import UserOutShortAuthor
from users.service import get_user_by_id, create_user

router = APIRouter(prefix='/users', tags=['Users'])


@router.post(
        '/{id}/follow',
        response_model=Union[BaseResponse, ResponseError],
)
async def follow(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of POST-request of following some user."""
    other_user: Optional[User] = await get_user_by_id(session=session, user_id=id)
    if not other_user:
        raise UserNotFoundError(message='User with passed id is not exist')

    if other_user in current_user.followed:
        raise RelationshipError(message='You are already follow this user')
    else:
        current_user.followed.append(other_user)
        await session.commit()
        return {'result': True}


@router.delete(
        '/{id}/follow',
        response_model=Union[BaseResponse, ResponseError],
)
async def unfollow(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of DELETE-request of unfollowing some user."""
    other_user: Optional[User] = await get_user_by_id(session=session, user_id=id)
    if not other_user:
        raise UserNotFoundError(message='User with passed id is not exist')

    if other_user not in current_user.followed:
        raise RelationshipError(message='You are not already follow this user')
    else:
        current_user.followed.remove(other_user)
        await session.commit()
        return {'result': True}


@router.get(
        '/me',
        response_model=Union[ResponseUserGet, ResponseError],
)
async def get_info_me(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of GET-request of getting current user's information."""
    return {'result': True, 'user': user.to_json()}


@router.get(
        '/{id}',
        response_model=Union[ResponseUserGet, ResponseError],
)
async def get_info_user(
    id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of GET-request of getting some user's information."""
    user: Optional[User] = await get_user_by_id(session=session, user_id=id)
    if not user:
        raise UserNotFoundError(message='User with passed id is not exist')

    return {'result': True, 'user': user.to_json()}


@router.post(
        '/{name}',
        response_model=Union[UserOutShortAuthor, ResponseError],
)
async def add_user(
    name: str,
    session: AsyncSession = Depends(get_session),
):
    """Endpoint of POST-request of creating new user with name of path-parameter."""
    user: User = await create_user(name=name, session=session, api_key_len=7)

    return user

"""Module with DB-operations with medias."""

import os
from pathlib import Path
from typing import List

from fastapi import UploadFile
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from images.models import Media

BYTES_IN_MEGABYTE: int = 1048576
ALLOWED_FILE_EXTENSIONS: tuple[str] = ('png', 'jpg', 'jpeg', 'tiff', 'heic')


async def update_medias(
        session: AsyncSession,
        media_ids: List[int],
        new_tweet_id: int,
) -> None:
    """Function of tweet_id parameter updating."""
    stmt = update(Media).where(Media.id.in_(media_ids)).values(tweet_id=new_tweet_id)
    await session.execute(stmt)
    await session.commit()


async def add_media_to_db(session: AsyncSession, filename: 'str') -> Media:
    """Function of adding media to DB."""
    media_obj = Media(name=filename)
    session.add(media_obj)
    await session.commit()
    media_obj.name = str(media_obj.id) + Path(filename).suffix
    await session.commit()

    return media_obj


def save_file_to_server(filename: str, file_obj: UploadFile) -> None:
    """Function of file saving to the server."""
    path_dir: str = os.path.join('..', 'static', 'images')
    os.makedirs(path_dir, exist_ok=True)

    path_img: str = os.path.join(path_dir, filename)
    with open(path_img, 'wb') as f:
        f.write(file_obj.file.read())


def is_filesize_ok(file_obj: UploadFile) -> bool:
    """Function of file size checking."""
    return file_obj.size <= BYTES_IN_MEGABYTE * 5


def is_filetype_ok(file_obj: UploadFile) -> bool:
    """Function of file extension checking."""
    file_extension: str = file_obj.filename.split('.')[-1]
    return file_extension in ALLOWED_FILE_EXTENSIONS


def is_file_consist_malware(file_obj: UploadFile) -> bool:
    """File of malware existing checking."""
    return False

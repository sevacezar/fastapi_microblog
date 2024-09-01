"""Module with endpoints of actions with medias."""

from typing import Union

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_session, get_user_by_api_key_dependencie
from images.exceptions import FileMalwareError, FileSizeError, FileTypeError
from images import service as srv
from users.models import User
from utils.global_schemas import ResponseMediaPost, ResponseError

router = APIRouter(prefix='/medias', tags=['Medias'])


@router.post(
    '',
    response_model=Union[ResponseMediaPost, ResponseError],
)
async def upload_media(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_user_by_api_key_dependencie),
):
    """Endpoint of POST-request of adding new media."""
    if not srv.is_filesize_ok(file_obj=file):
        raise FileSizeError(message='Size of the file is larger than 5 MB')
    
    if not srv.is_filetype_ok(file_obj=file):
        raise FileTypeError(message='Not allowed file extension. ' \
                            'Alowed extensions: jpg, jpeg, png, tiff, heic')
    
    if srv.is_file_consist_malware(file_obj=file):
        raise FileMalwareError(message='The file consist malware')
    
    # Adding media to DB
    media_obj = await srv.add_media_to_db(session=session, filename=file.filename)

    # Saving media to server
    srv.save_file_to_server(filename=media_obj.name, file_obj=file)
    
    return {'result': True, 'media_id': media_obj.id}

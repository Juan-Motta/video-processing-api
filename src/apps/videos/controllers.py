import logging
import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.auth.utils import get_authorization_header
from src.apps.commons.exceptions import CustomException
from src.apps.commons.schemas import BaseErrorSchema, UnexpectedErrorSchema
from src.apps.tasks.models import Task, TaskStatusEnum
from src.apps.users.models import User
from src.apps.videos.models import Video
from src.apps.videos.schemas import GetVideoOutputSchema
from src.core.database.dependencies import get_db
from src.core.gcp.cloud_storage.base import GCPCloudStorage
from src.settings.base import settings

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(tags=["Videos"])

METADATA = {
    "name": "Videos",
    "description": """Endpoints creados para la obtencion de videos""",
}


@router.get(
    "",
    response_model=list[GetVideoOutputSchema],
    responses={
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def get_videos(
    max: int = 10,
    order: int = 0,
    session: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_authorization_header),
):
    """
    Permite consultar la información de todos los vídeos disponibles en la
    aplicación.
    """
    query = select(User).where(User.id == jwt_payload["id"], User.is_active == True)
    user = session.execute(query).scalars().first()
    if not user:
        raise CustomException(
            error="error_user",
            message="Usuario no encontrado",
            status_code=404,
        )
    query = select(Task).where(
        Task.is_active == True, Task.status == TaskStatusEnum.PROCESSED
    )
    if order == 0:
        query = query.order_by(Task.id.asc())
    else:
        query = query.order_by(Task.id.desc())
    query = query.limit(max)
    tasks = session.execute(query).scalars().all()
    return [
        GetVideoOutputSchema(
            id=task.processed_video.id,
            title=task.processed_video.title,
            user_id=task.processed_video.user_id,
            filename=task.processed_video.filename,
            url=f"{settings.BACKEND_URL}/api/videos/download/{task.processed_video.id}",
            score=task.processed_video.score,
        )
        for task in tasks
    ]


@router.get(
    "/download/{video_id}",
    responses={
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def download_video(
    video_id: int,
    session: Session = Depends(get_db),
):
    """
    Permite descargar un video en formato mp4.
    """
    query = select(Video).where(Video.id == video_id)
    video = session.execute(query).scalars().first()
    if not video:
        raise CustomException(
            error="error_video",
            message="Video no encontrado",
            status_code=404,
        )
    client = GCPCloudStorage()
    bucket_name = settings.VIDEOS_BUCKET
    cloud_path = video.url

    try:
        video_bytes = client.download_file_as_bytes(
            bucket_name=bucket_name, source_path=cloud_path
        )
    except Exception as e:
        logger.exception(e)
        raise CustomException(
            error="error_video",
            message="Error al descargar el video desde Cloud Storage",
            status_code=500,
        ) from e

    return StreamingResponse(iter([video_bytes]), media_type="video/mp4")

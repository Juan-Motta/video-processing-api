import logging
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.auth.utils import get_authorization_header
from src.apps.commons.exceptions import CustomException
from src.apps.commons.schemas import BaseErrorSchema, UnexpectedErrorSchema
from src.apps.tasks.models import Task, TaskStatusEnum
from src.apps.tasks.schemas import (
    CreateTaskOutputSchema,
    DeleteTaskOutputSchema,
    GetAllTaskOutputSchema,
    GetTaskOutputSchema,
    GetTaskVideoOutputSchema,
)
from src.apps.tasks.tasks import process_video
from src.apps.users.models import User
from src.apps.videos.models import Video
from src.core.database.dependencies import get_db
from src.core.gcp.cloud_storage.base import GCPCloudStorage
from src.core.gcp.pubsub.handlers import PubSubEvents
from src.core.gcp.pubsub.publisher import PubSubPublisher
from src.settings.base import settings

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(tags=["Tasks"])

METADATA = {
    "name": "Tasks",
    "description": """Endpoints creados para el manejo de tareas pesadas""",
}


@router.get(
    "",
    response_model=list[GetAllTaskOutputSchema],
    responses={
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def get_tasks(
    max: int = 10,
    order: int = 0,
    session: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_authorization_header),
):
    """
    Permite recuperar todas las tareas de edición de un usuario autorizado en
    la aplicación.
    """
    query = select(User).where(User.id == jwt_payload["id"], User.is_active == True)
    user = session.execute(query).scalars().first()
    if not user:
        raise CustomException(
            error="error_user",
            message="Usuario no encontrado",
            status_code=404,
        )
    query = select(Task).where(Task.user_id == user.id, Task.is_active == True)
    if order == 0:
        query = query.order_by(Task.id.asc())
    else:
        query = query.order_by(Task.id.desc())
    query = query.limit(max)
    tasks = session.execute(query).scalars().all()
    return [
        GetAllTaskOutputSchema(
            id=task.id,
            task_id=task.task_id,
            user_id=task.user_id,
            original_video_id=task.original_video_id,
            processed_video_id=task.processed_video_id,
            status=task.status.value,
            created_at=task.created_at,
            updated_at=task.updated_at,
            is_active=task.is_active,
        )
        for task in tasks
    ]


@router.get(
    "/{task_id}",
    response_model=GetTaskOutputSchema,
    responses={
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def get_tasks(
    task_id: int,
    session: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_authorization_header),
):
    """
    Permite recuperar la información de una tarea concreta perteneciente a un
    usuario, para lo cual se requiere autorización.
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
        Task.user_id == user.id, Task.id == task_id, Task.is_active == True
    )
    task = session.execute(query).scalars().first()
    if not task:
        raise CustomException(
            error="error_task",
            message="Tarea no encontrada",
            status_code=404,
        )
    return GetTaskOutputSchema(
        id=task.id,
        task_id=task.task_id,
        user_id=task.user_id,
        original_video=GetTaskVideoOutputSchema(
            title=task.original_video.title,
            user_id=task.original_video.user_id,
            filename=task.original_video.filename,
            url=f"{settings.BACKEND_URL}/api/videos/download/{task.original_video.id}",
            score=task.original_video.score,
        ),
        processed_video=(
            GetTaskVideoOutputSchema(
                title=task.processed_video.title,
                user_id=task.processed_video.user_id,
                filename=task.processed_video.filename,
                url=f"{settings.BACKEND_URL}/api/videos/download/{task.processed_video.id}",
                score=task.processed_video.score,
            )
            if task.processed_video
            else None
        ),
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at,
        is_active=task.is_active,
    )


@router.post(
    "",
    response_model=CreateTaskOutputSchema,
    responses={
        400: {"description": "Unsuccesful response", "model": BaseErrorSchema},
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def create_task(
    file: UploadFile,
    session: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_authorization_header),
):
    """
    Permite crear una nueva tarea de edición de video. El usuario requiere
    autorización.
    """
    query = select(User).where(User.id == jwt_payload["id"], User.is_active == True)
    user = session.execute(query).scalars().first()
    if not user:
        raise CustomException(
            error="error_user",
            message="Usuario no encontrado",
            status_code=404,
        )
    # Crear directorio para guardar el video
    video_uuid = str(uuid.uuid4())
    valid_extensions = ["mp4"]
    file_extension = file.filename.split(".")[-1]
    if not file_extension:
        raise CustomException(
            error="error_video",
            message="Extension de video no encontrada",
            status_code=400,
        )
    if file_extension not in valid_extensions:
        raise CustomException(
            error="error_video",
            message="Formato de video no permitido",
            status_code=400,
        )
    # Guardar video
    client = GCPCloudStorage()
    public_url = client.upload_file(
        bucket_name=settings.VIDEOS_BUCKET,
        file=file.file,
        destination_path=f"{video_uuid}/{file.filename}",
    )
    logger.info(f"Video guardado en {video_uuid}/{file.filename}")
    video = Video(
        title=f"""video {user.username} {datetime.now().strftime("%d_%m_%Y")}""",
        user_id=user.id,
        filename=file.filename,
        url=f"{video_uuid}/{file.filename}",
        score=None,
    )
    session.add(video)
    session.flush()
    # Crear tarea
    task = Task(
        task_id=video_uuid,
        user_id=user.id,
        original_video_id=video.id,
        processed_video_id=None,
    )
    session.add(task)
    session.flush()
    session.commit()
    logger.info(f"Registro de tarea creado {task.id}")
    client = PubSubPublisher()
    response = client.run(
        data={"video_id": video.id, "task_id": task.id},
        event_type=PubSubEvents.PROCESS_VIDEO,
    )
    # response = process_video.apply_async((video.id, task.id), task_id=task.task_id)
    logger.info(f"Tarea creada {response}")
    task.status = TaskStatusEnum.UPLOADED
    session.commit()
    return CreateTaskOutputSchema(
        id=task.id,
        task_id=task.task_id,
        message="Tarea creada exitosamente",
    )


@router.delete(
    "/{task_id}",
    response_model=DeleteTaskOutputSchema,
    responses={
        400: {"description": "Unsuccesful response", "model": BaseErrorSchema},
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def delete_task(
    task_id: int,
    session: Session = Depends(get_db),
    jwt_payload: dict = Depends(get_authorization_header),
):
    """
    Permite eliminar una tarea en la aplicación. El usuario requiere
    autorización.
    """
    query = select(User).where(User.id == jwt_payload["id"], User.is_active == True)
    user = session.execute(query).scalars().first()
    if not user:
        raise CustomException(
            error="error_user",
            message="Usuario no encontrado",
            status_code=404,
        )
    query = select(Task).where(Task.user_id == user.id, Task.id == task_id)
    task = session.execute(query).scalars().first()
    if not task:
        raise CustomException(
            error="error_task",
            message="Tarea no encontrada",
            status_code=404,
        )
    if task.status != TaskStatusEnum.PROCESSED:
        raise CustomException(
            error="error_task",
            message="No se puede eliminar una tarea en procesamiento",
            status_code=400,
        )
    task.is_active = False
    session.commit()
    return DeleteTaskOutputSchema(
        message="Tarea eliminada exitosamente",
        id=task.id,
        task_id=task.task_id,
        is_active=task.is_active,
    )

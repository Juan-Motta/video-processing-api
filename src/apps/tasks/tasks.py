import logging
import os
import tempfile
from datetime import datetime

from moviepy.editor import (
    ColorClip,
    CompositeVideoClip,
    ImageClip,
    VideoFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx.all import resize
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.apps.tasks.models import Task, TaskStatusEnum
from src.apps.users.models import User
from src.apps.videos.models import Video
from src.celery_worker import celery
from src.core.database.dependencies import get_db
from src.core.gcp.cloud_storage.base import GCPCloudStorage
from src.settings.base import settings

logger = logging.getLogger(__name__)


# @celery.task
def process_video(video_id, task_id) -> None:
    logger.info(f"Procesando video {video_id} asociado a la tarea {task_id}")
    try:
        logger.info("Conectando con la base de datos")
        session: Session = next(get_db())
    except Exception as e:
        logger.info(f"Error al conectar con la base de datos {e}")
        logger.exception(e)
        return
    logger.info("Conexión exitosa con la base de datos")
    # Recupera registros de video y tarea de la base de datos
    query = select(Video).where(Video.id == video_id)
    original_video = session.execute(query).scalars().first()
    query = select(Task).where(Task.id == task_id)
    task = session.execute(query).scalars().first()
    # Validar que existan los registros
    if not original_video or not task:
        logger.info("Video no encontrado")
        return
    logger.info(f"Video encontrado {original_video.id}")
    logger.info(f"Task encontrado {task.id}")
    # Iniciar procesamiento
    client = GCPCloudStorage()
    try:
        logger.info(f"Descargando video {original_video.url}")
        file = client.download_file(
            bucket_name=settings.VIDEOS_BUCKET, source_path=original_video.url
        )
        logger.info(f"Video descargado {file}")
        # Obtener video original
        logger.info("Procesando video")
        video = VideoFileClip(file)
        # Recortar video a 20 segundos
        video = video.subclip(0, 20)
        # Redimensionar video a un formato de 16:9
        video = resize(video, height=video.w * 9 / 16)
        # Crear una pantalla negra (ColorClip) con la misma resolución que el video
        black_screen = ColorClip(
            size=video.size, color=(0, 0, 0), duration=3
        )  # Black screen for 2 seconds
        # Cargar el logo y redimensionarlo si es necesario
        logo = ImageClip(
            f"{os.getcwd()}/statics/logo_256.png", duration=2
        )  # Cambia el tamaño según sea necesario
        # Colocar el logo en el centro de la pantalla negra
        logo_on_black = CompositeVideoClip([black_screen, logo.set_position("center")])
        # Aplica una transición de fadeout de 0.5 segundo al video y a la pantalla negra con el logo
        video_with_transition = video.crossfadeout(0.5)
        # Aplica una transición de fadein de 1 segundo a la pantalla negra con el logo
        logo_on_black_with_transition = logo_on_black.crossfadein(1)
        # Combinar el video recortado con la pantalla negra y el logo, con transición de 1 segundo
        final_clip = concatenate_videoclips(
            [video_with_transition, logo_on_black_with_transition], method="compose"
        )
        logger.info("Video procesado")
        # Almacenar video procesado
        temp_dir = tempfile.mkdtemp()
        processed_video_path = os.path.join(
            temp_dir, f"processed_{original_video.filename}"
        )

        final_clip.write_videofile(
            processed_video_path,
            codec="libx264",
            fps=24,
        )
        logger.info(f"Video procesado guardado en {processed_video_path}")
        destination_blob_name = f"{task.task_id}/processed_{original_video.filename}"
        client.upload_file(
            bucket_name=settings.VIDEOS_BUCKET,
            destination_path=destination_blob_name,
            file_path=processed_video_path,
        )
        logger.info(f"Video procesado guardado en {destination_blob_name}")
        # Generar registro de video procesado
        processed_video = Video(
            title=f"""video {task.user.username} {datetime.now().strftime("%d_%m_%Y")}""",
            user_id=task.user.id,
            filename=f"processed_{original_video.filename}",
            url=destination_blob_name,
            score=None,
        )
    except Exception as e:
        logger.exception(e)
        task.status = TaskStatusEnum.FAILURE
        session.commit()
        return
    # Actualizar tarea con video procesado
    session.add(processed_video)
    session.flush()
    task.status = TaskStatusEnum.PROCESSED
    task.processed_video_id = processed_video.id
    session.commit()

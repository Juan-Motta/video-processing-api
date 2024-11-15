import base64
import json
import logging

from google.cloud import pubsub_v1  # type: ignore
from google.cloud.pubsub_v1.subscriber.message import Message  # type: ignore
from google.cloud.pubsub_v1.types import FlowControl  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore

from src.apps.tasks.tasks import process_video
from src.core.database.dependencies import get_db
from src.core.gcp.pubsub.schemas import PubSubEventMessage
from src.settings.base import settings

logger = logging.getLogger(__name__)


def callback(message: Message, *args, **kwargs):
    """
    Ejecuta el procesamiento asíncrono del mensaje y reconoce el mensaje.

    Esta función intenta obtener el event lopp actual o crear uno nuevo si
    no existe. Luego, ejecuta la función de callback asíncrona utilizando el event
    loop. Si ocurre un error durante el procesamiento del mensaje, se captura
    y se registra en el log. Finalmente, una vez la funcion es procesadareconoce
    el mensaje.

    Args:
        message (Message): El mensaje recibido de Pub/Sub.
    """
    try:
        raw_message = json.loads(message.data.decode("utf-8"))
        logger.info(f"Received message: {raw_message}")
        processed_message = PubSubEventMessage(**raw_message)
        logger.info(f"Processing message: {processed_message}")
        process_video(
            video_id=processed_message.data["video_id"],
            task_id=processed_message.data["task_id"],
        )
        logger.info("Message processed successfully")
    except Exception as e:
        logger.info("Error processing message")
        logger.exception(e)
    message.ack()
    logger.info("Message acknowledged...")


def get_pubsub_credentials():
    """
    Obtiene las credenciales de Pub/Sub desde una cadena codificada en base64.

    Esta función decodifica una cadena base64 que contiene las credenciales del
    servicio de Google Cloud y crea un objeto de credenciales.

    Returns:
        Credentials: Las credenciales de servicio de Google Cloud.
    """
    logger.info("Getting pubsub credentials...")
    account_info = json.loads(base64.b64decode(settings.GCP_CREDENTIALS_BASE64))
    credentials = Credentials.from_service_account_info(account_info)
    return credentials


def run_pubsub_subscriber():
    """
    Configura y ejecuta un suscriptor de Pub/Sub.

    Esta función crea un cliente suscriptor de Pub/Sub utilizando las credenciales
    obtenidas, se suscribe a un tópico especificado y procesa los mensajes entrantes.
    También maneja la cancelación en caso de una interrupción del teclado (Ctrl+C).
    """
    with pubsub_v1.SubscriberClient(credentials=get_pubsub_credentials()) as subscriber:
        logger.info(f"Subscribing to topic {settings.PUBSUB_SUBSCRIPTION_ID}...")
        subscription_path = subscriber.subscription_path(
            settings.GCP_PROJECT_ID, settings.PUBSUB_SUBSCRIPTION_ID
        )
        # max_messages especifica el número máximo de mensajes que el subscriptor
        # puede manejar simultáneamente.
        future = subscriber.subscribe(
            subscription_path,
            callback=callback,
            flow_control=FlowControl(max_messages=1),
        )
        try:
            future.result()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            future.cancel()
            future.result()

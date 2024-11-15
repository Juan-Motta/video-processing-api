import base64
import json
import logging
from typing import Any

from google.cloud import pubsub_v1  # type: ignore
from google.oauth2.service_account import Credentials  # type: ignore

from src.core.gcp.pubsub.handlers import PubSubEvents
from src.core.gcp.pubsub.schemas import PubSubEventMessage
from src.settings.base import settings

logger = logging.getLogger(__name__)


class PubSubPublisher:
    """
    Clase para publicar mensajes en Google Cloud Pub/Sub.

    Esta clase maneja la publicación de eventos en un tópico de Pub/Sub,
    incluyendo la inicialización del servicio, el envío de mensajes y
    el registro de eventos.

    Métodos:
    --------
    __start_publisher():
        Inicializa el cliente de publicación de Pub/Sub con las credenciales
        proporcionadas en la configuración.

    __send_message():
        Envía un mensaje al tópico de Pub/Sub con los datos del evento.

    run(data: dict[str, Any], event_type: str):
        Ejecuta el proceso completo de publicación de un evento, incluyendo
        la inicialización del servicio, el registro del evento y el envío del
        mensaje a Pub/Sub.

    Atributos:
    ----------
    publisher : PublisherClient
        Cliente de Pub/Sub utilizado para publicar mensajes.
    data : dict[str, Any]
        Datos del evento a ser publicado.
    event_type : str
        Tipo de evento a ser publicado.
    event_log : PubSubEvent
        Registro del evento en la base de datos.
    future : Future
        Objeto que representa el resultado futuro de la publicación del mensaje.
    """

    def __start_publisher(self):
        logger.info("Initializing Pub/Sub service...")
        if not settings.GCP_CREDENTIALS_BASE64:
            raise ValueError("GCP credentials not found")
        if not settings.GCP_PROJECT_ID:
            raise ValueError("GCP project ID not found")
        if not settings.PUBSUB_TOPIC_ID:
            raise ValueError("Pub/Sub topic ID not found")
        account_info = json.loads(base64.b64decode(settings.GCP_CREDENTIALS_BASE64))
        credentials = Credentials.from_service_account_info(account_info)
        self.publisher = pubsub_v1.PublisherClient(credentials=credentials)

    def __send_message(self):
        topic_path = self.publisher.topic_path(
            settings.GCP_PROJECT_ID, settings.PUBSUB_TOPIC_ID
        )
        data = PubSubEventMessage(event_type=self.event_type, data=self.data)
        message = json.dumps(data.model_dump()).encode("utf-8")
        self.future = self.publisher.publish(topic_path, message)

    def run(self, data: dict[str, Any], event_type: str):
        self.data = data
        self.event_type = event_type

        if self.event_type not in list(PubSubEvents):
            raise ValueError(f"Event type {self.event_type} not found")

        try:
            self.__start_publisher()
            self.__send_message()
        except Exception as e:
            logger.error(e)
            raise e

        return self.future.result()

import logging

from sqlalchemy.orm import Session

from src.celery_worker import celery

logger = logging.getLogger(__name__)


@celery.task
def dummy_task() -> None:
    logger.info("Dummy task executed")


async def dummy_event_handler(data: dict, session: Session, *args, **kwargs):
    logger.info("Dummy task executed")
    logger.info(data)
    pass

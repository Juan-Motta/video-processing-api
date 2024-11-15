import logging

from celery import Celery

from src.settings.base import settings

# Initialize Celery
celery: Celery = Celery(
    __name__,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BROKER_URL,
)

# Auto-discover tasks
celery.autodiscover_tasks(["src.apps.commons.tasks", "src.apps.tasks.tasks"])

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Set Celery's logger to DEBUG
celery_logger = logging.getLogger("celery")
celery_logger.setLevel(logging.DEBUG)

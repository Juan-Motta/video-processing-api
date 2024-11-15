import logging

from src.settings.base import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL, format="%(levelname)s:     %(message)s"
    )
    logging.getLogger("multipart").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

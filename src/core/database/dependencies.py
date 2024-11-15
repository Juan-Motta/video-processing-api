import logging
from typing import Generator

from sqlalchemy.orm import Session

from src.core.database.base import session

logger = logging.getLogger(__name__)


def get_db() -> Generator[Session, None, None]:
    logger.info("Generating database session")
    db = session()
    try:
        yield db
    except Exception as e:
        logger.error(f"Error while generating database session {e}")
        logger.exception(e)
    finally:
        logger.info("Closing database session")
        db.close()

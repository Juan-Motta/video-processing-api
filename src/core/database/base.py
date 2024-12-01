from datetime import datetime
from enum import Enum
from typing import Any, Dict

import sqlalchemy as sa
from sqlalchemy import Engine, create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy_json import mutable_json_type

from src.settings.base import settings

engine: Engine = create_engine(sa.engine.url.URL(
    drivername=settings.DB_DRIVER,
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    query={"unix_sock": settings.DB_URL_SOCKET},
))

session: sessionmaker[Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class Base(DeclarativeBase):
    type_annotation_map = {
        Enum: sa.Enum(Enum, native_enum=False, validate_strings=True),
        datetime: sa.TIMESTAMP(timezone=True),
        Dict[str, Any]: mutable_json_type(dbtype=postgresql.JSONB, nested=True),
    }
    metadata = sa.MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

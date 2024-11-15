import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database.base import Base
from src.core.database.dependencies import get_db
from src.main import app  # type: ignore
from src.settings.base import settings

TEST_DATABASE_URL: str = settings.DB_URL_TEST
main_app = app


def start_application():
    return main_app


SQLALCHEMY_DATABASE_URL = TEST_DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def app():
    """
    Crea una base de datos nueva para cada caso de pruebas
    """
    Base.metadata.create_all(engine)
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(app: FastAPI):
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(app: FastAPI, db_session: SessionTesting):  # type: ignore
    """
    Crea un nuevo TestClient de FastAPI que usa el fixture `db_session` para
    sobreescribir la dependencia `get_db` que es inyectada en las rutas.
    """

    def _get_test_db():
        return db_session

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client

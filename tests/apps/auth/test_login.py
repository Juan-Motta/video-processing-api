from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.apps.auth.utils import encrypt_password
from src.apps.tasks.models import Task
from src.apps.users.models import User
from src.apps.videos.models import Video

faker = Faker()


def test_login_ok_with_username(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user1 = User(
        username=username,
        email=email,
        password=encrypt_password(password),
    )
    db_session.add(user1)
    db_session.flush()

    response = client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["access_token"] is not None


def test_login_ok_with_email(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user1 = User(
        username=username,
        email=email,
        password=encrypt_password(password),
    )
    db_session.add(user1)
    db_session.flush()

    response = client.post(
        "/api/auth/login", json={"username": email, "password": password}
    )
    data = response.json()
    assert response.status_code == 200
    assert data["access_token"] is not None


def test_login_with_invalid_user(client: TestClient, db_session: Session):
    response = client.post(
        "/api/auth/login",
        json={"username": faker.user_name(), "password": faker.password()},
    )
    data = response.json()
    assert response.status_code == 404
    assert data["message"] == "Usuario no encontrado"


def test_login_with_invalid_credentials(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    user1 = User(
        username=username,
        email=email,
        password=encrypt_password(password),
    )
    db_session.add(user1)
    db_session.flush()

    response = client.post(
        "/api/auth/login", json={"username": username, "password": faker.password()}
    )
    data = response.json()
    assert response.status_code == 403
    assert data["message"] == "Credenciales inválidas"

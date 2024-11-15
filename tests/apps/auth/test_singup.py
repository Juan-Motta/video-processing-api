from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.apps.auth.utils import encrypt_password
from src.apps.tasks.models import Task
from src.apps.users.models import User
from src.apps.videos.models import Video

faker = Faker()


def test_signup_ok(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 200
    assert data["email"] == email
    assert data["username"] == username


def test_signup_with_invalid_username(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    response = client.post(
        "/api/auth/signup",
        json={
            "username": "",
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "nombre de usuario es requerido"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": faker.user_name()[0],
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "nombre de usuario es muy corto"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": faker.user_name() * 10,
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "nombre de usuario es muy largo"


def test_signup_with_invalid_email(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": "",
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "email es requerido"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": faker.email() * 10,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "email es demasiado largo"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": faker.word(),
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "email no es válido"


def test_signup_with_invalid_password(client: TestClient, db_session: Session):
    username = faker.user_name()
    email = faker.email()
    password = faker.password()

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": "",
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "contraseña es requerida"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": password,
            "password2": "",
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "contraseña es requerida"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": "a",
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "contraseña es muy corta"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": password * 10,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "contraseña es muy larga"

    response = client.post(
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": faker.password(),
            "password2": faker.password(),
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "contraseñas no coinciden"


def test_signup_with_existing_user(client: TestClient, db_session: Session):
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
        "/api/auth/signup",
        json={
            "username": username,
            "email": email,
            "password1": password,
            "password2": password,
        },
    )
    data = response.json()
    assert response.status_code == 400
    assert data["message"] == "Usuario ya se encuentra registrado"

import logging
import re

import jwt
from fastapi import APIRouter, Depends, Request
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from src.apps.auth.schemas import (
    LoginInputSchema,
    LoginOutputSchema,
    SignupInputSchema,
    SignupOutputSchema,
)
from src.apps.auth.utils import encrypt_password, validate_password
from src.apps.commons.exceptions import CustomException
from src.apps.commons.schemas import BaseErrorSchema, UnexpectedErrorSchema
from src.apps.users.models import User
from src.core.database.dependencies import get_db
from src.settings.base import settings

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(tags=["Authentication"])

METADATA = {
    "name": "Authentication",
    "description": """Endpoints creados para la autenticación y
    creacion de usuarios""",
}


@router.post(
    "/login",
    response_model=LoginOutputSchema,
    responses={
        403: {
            "description": "Unauthorized response",
            "model": BaseErrorSchema,
        },
        404: {"description": "Not found response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def login(body: LoginInputSchema, session: Session = Depends(get_db)):
    """
    Permite iniciar sesión y obtener el token de autorización para consumir los
    recursos del API, suministrando el nombre de usuario y la contraseña de
    una cuenta previamente registrada.
    """
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(email_regex, body.username):
        query = select(User).where(User.email == body.username)
    else:
        query = select(User).where(User.username == body.username)
    user = session.execute(query).scalars().first()
    if user is None:
        raise CustomException(
            error="error_auth",
            message="Usuario no encontrado",
            status_code=404,
        )
    is_valid_password = validate_password(body.password, user.password)
    if not is_valid_password:
        raise CustomException(
            error="error_auth",
            message="Credenciales inválidas",
            status_code=403,
        )
    token = jwt.encode(
        {"id": user.id, "email": user.email, "username": user.username},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return LoginOutputSchema(access_token=token).model_dump()


@router.post(
    "/signup",
    response_model=SignupOutputSchema,
    responses={
        400: {"description": "Unsuccesful response", "model": BaseErrorSchema},
        500: {
            "description": "Unexpected error response",
            "model": UnexpectedErrorSchema,
        },
    },
)
async def create_user(body: SignupInputSchema, session: Session = Depends(get_db)):
    """
    Permite crear una cuenta con los campos para nombre de usuario, correo
    electrónico y contraseña. El nombre y el correo electrónico deben ser
    únicos en la plataforma, mientras que la contraseña debe seguir unos
    lineamientos mínimos de seguridad. Adicionalmente, la clave debe ser
    solicitada dos veces para que el usuario confirme que la ingresa de forma
    correcta.
    """
    query = select(User).where(
        or_(User.username == body.username, User.email == body.email)
    )
    user = session.execute(query).scalars().first()

    if user:
        raise CustomException(
            error="error_auth",
            message="Usuario ya se encuentra registrado",
            status_code=400,
        )

    hashed_password = encrypt_password(password=body.password1)
    user = User(username=body.username, email=body.email, password=hashed_password)
    session.add(user)
    session.commit()

    return SignupOutputSchema(
        message="Usuario creado exitosamente",
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    ).model_dump()

import base64
import hashlib
import hmac
import logging
import os

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.apps.commons.exceptions import CustomException
from src.settings.base import settings

logger = logging.getLogger(__name__)


def pbkdf2(password, salt, iterations=260000, dklen=32, hash_name="sha256"):
    """
    Imita el hashing de contraseñas de Django (PBKDF2).
    Args:
    - password: Contraseña a ser hasheada (in bytes).
    - salt: Sal usado para hashing (in bytes).
    - iterations: Numero de iteraciones para el algoritmo PBKDF2.
    - dklen: Longitud del string resultante.
    - hash_name: Hash para el algormitmo (default is sha256).

    Returns:
    - String resultante en base64 encoding.
    """
    dk = hashlib.pbkdf2_hmac(hash_name, password, salt, iterations, dklen)
    return base64.b64encode(dk).decode("ascii")


def encrypt_password(password, salt=None, iterations=260000):
    """
    Encripta una contraseña similar al mecanismo por defecto de Django.
    Args:
    - password: Contraseña en texto plano (string).
    - salt: String usado como salt (Si no se proporciona se genera uno nuevo).
    - iterations: Numero de iteraciones para el algoritmo PBKDF2.

    Returns:
    - Un stringque combina las iteraciones, salt y la contraseña hasheada en el formato:
      "pbkdf2_sha256$iterations$salt$hash".
    """
    # Generate salt if not provided
    if salt is None:
        salt = base64.b64encode(os.urandom(16)).decode("ascii").strip()

    # Convert password to bytes
    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("ascii")

    # Generate hashed password
    hashed_password = pbkdf2(password_bytes, salt_bytes, iterations=iterations)

    # Return the format used by Django
    return f"pbkdf2_sha256${iterations}${salt}${hashed_password}"


def validate_password(password, stored_password):
    """
    Valida una contraseña dada contra la contraseña hasheada almacenada.
    Args:
    - password: Contraseña proporcionada en texto plano (string).
    - stored_password: Hash de la contrasen1a del usuario almacenada "pbkdf2_sha256$iterations$salt$hash" (string).

    Returns:
    - True si la contraseña es valida, False en otro caso.
    """
    # Split the stored password into components
    algorithm, iterations, salt, stored_hash = stored_password.split("$")

    # Ensure we are dealing with the correct algorithm
    if algorithm != "pbkdf2_sha256":
        raise ValueError("Unsupported algorithm")

    # Convert iterations to integer
    iterations = int(iterations)

    # Convert password and salt to bytes
    password_bytes = password.encode("utf-8")
    salt_bytes = salt.encode("ascii")

    # Hash the user-provided password using the same salt and iterations
    hashed_password = pbkdf2(password_bytes, salt_bytes, iterations)

    # Compare the stored hash with the newly hashed password
    return hmac.compare_digest(hashed_password, stored_hash)


async def get_authorization_header(
    request: Request,
    bearer: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
):
    header = request.headers.get("Authorization")
    if not header:
        raise CustomException(
            error="auth_error",
            message="Cabecera de autenticacion es requerida",
            status_code=401,
        )
    key, token = header.split(" ")
    if key != "Bearer":
        raise CustomException(
            error="auth_error",
            message="Tipo de cabecera de autenticacion invalida",
            status_code=401,
        )
    if not token:
        raise CustomException(
            error="auth_error", message="Token invalido", status_code=401
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        raise CustomException(
            error="auth_error", message="Token invalido", status_code=401
        )
    return payload

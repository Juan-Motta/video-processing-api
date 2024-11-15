import re

from pydantic import BaseModel, ValidationError, field_validator, model_validator
from pydantic_core import PydanticCustomError


class LoginInputSchema(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value:
            raise PydanticCustomError(
                "error_auth", "Nombre de usuario es requerido", None
            )
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str):
        if not value:
            raise PydanticCustomError("error_auth", "Contraseña es requerida", None)
        return value


class LoginOutputSchema(BaseModel):
    access_token: str


class SignupInputSchema(BaseModel):
    username: str
    email: str
    password1: str
    password2: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str):
        if not value:
            raise PydanticCustomError(
                "error_auth", "Nombre de usuario es requerido", None
            )
        if len(value) < 2:
            raise PydanticCustomError(
                "error_auth", "Nombre de usuario es muy corto", None
            )
        if len(value) > 20:
            raise PydanticCustomError(
                "error_auth", "Nombre de usuario es muy largo", None
            )
        return value.strip().lower()

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str):
        if not value:
            raise PydanticCustomError("error_auth", "Email es requerido", None)
        if len(value) > 100:
            raise PydanticCustomError("error_auth", "Email es demasiado largo", None)
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, value):
            raise PydanticCustomError("error_auth", "Email no es válido", None)
        return value.strip().lower()

    @field_validator("password1", "password2")
    @classmethod
    def validate_password(cls, value: str):
        if not value:
            raise PydanticCustomError("error_auth", "Contraseña es requerida", None)
        if len(value) < 5:
            raise PydanticCustomError("error_auth", "Contraseña es muy corta", None)
        if len(value) > 20:
            raise PydanticCustomError("error_auth", "Contraseña es muy larga", None)
        return value

    @model_validator(mode="after")
    def validate_passwords_match(self):
        if self.password1 != self.password2:
            raise PydanticCustomError("error_auth", "Contraseñas no coinciden", None)
        return self


class SignupOutputSchema(BaseModel):
    message: str
    id: int
    username: str
    email: str
    is_active: bool

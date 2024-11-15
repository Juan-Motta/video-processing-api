from typing import Any

from pydantic import BaseModel


class UnexpectedErrorSchema(BaseModel):
    error: str | None = None
    message: str | None = None
    details: Any | None = None
    datetime: str


class BaseErrorSchema(BaseModel):
    error: str | None = None
    message: str | None = None
    loc: str | tuple | None = None
    input: str | dict | None = None
    ctx: dict | None = None
    datetime: str

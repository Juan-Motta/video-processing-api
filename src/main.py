import logging
import traceback
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.apps.auth.controllers import METADATA as auth_metadata
from src.apps.commons.exceptions import CustomException
from src.apps.commons.schemas import BaseErrorSchema, UnexpectedErrorSchema
from src.apps.dummy.controllers import METADATA as dummy_metadata
from src.apps.tasks.controllers import METADATA as tasks_metadata
from src.apps.videos.controllers import METADATA as videos_metadata
from src.core.logger.base import setup_logging
from src.routes import router
from src.settings.base import settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    yield


_openapi = FastAPI.openapi


def openapi(self: FastAPI):
    """
    Remueve el error 422 de la documentación de OpenAPI.
    """
    _openapi(self)

    for _, method_item in self.openapi_schema.get("paths").items():
        for _, param in method_item.items():
            responses = param.get("responses")
            # remove 422 response, also can remove other status code
            if "422" in responses:
                del responses["422"]

    return self.openapi_schema


FastAPI.openapi = openapi

app: FastAPI = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    dependencies=[],
    openapi_tags=[auth_metadata, tasks_metadata, videos_metadata, dummy_metadata],
)


@app.get("/")
async def root():
    return {"message": "OK"}


app.include_router(router, prefix="/api")


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=UnexpectedErrorSchema(
            error="unexpected_error",
            message=str(exc),
            details=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
            datetime=datetime.now().isoformat(),
        ).model_dump(),
    )


@app.exception_handler(CustomException)
async def exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code or 400,
        content=BaseErrorSchema(
            error=exc.error,
            message=exc.message,
            loc=None,
            input=None,
            ctx=None,
            datetime=datetime.now().isoformat(),
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def exception_handler1(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=BaseErrorSchema(
            error=f"""{exc.errors()[0].get("type").lower()}""",
            message=f"""{exc.errors()[0].get("msg").lower()}""",
            loc=exc.errors()[0].get("loc"),
            input=exc.errors()[0].get("input"),
            ctx=exc.errors()[0].get("ctx"),
            datetime=datetime.now().isoformat(),
        ).model_dump(),
    )

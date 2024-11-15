import logging

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.apps.dummy.tasks import dummy_task
from src.core.database.dependencies import get_db

logger = logging.getLogger(__name__)

router: APIRouter = APIRouter(tags=["Dummy"])

METADATA = {
    "name": "Dummy",
    "description": """Endpoints creados para pruebas de concepto
    de funcionalidades asociadas a la aplicación y al framework""",
}


@router.get("/health-check")
async def health_check(request: Request, session: Session = Depends(get_db)):
    logger.info("Health check")
    return {"message": "OK"}


@router.post("/auth")
async def health_check(request: Request, session: Session = Depends(get_db)):
    logger.info("Health check")
    return {"message": "OK"}


@router.get("/task")
async def start_dummy_task(request: Request, session: Session = Depends(get_db)):
    response = dummy_task.delay()
    return {"status": response.status, "task_id": response.id}


@router.get("/task-state")
async def start_dummy_task(request: Request, session: Session = Depends(get_db)):
    response = AsyncResult(request.query_params["task_id"])
    return {"status": response.status, "task_id": response.id}

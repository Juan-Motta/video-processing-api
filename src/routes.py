from fastapi import APIRouter

from src.apps.auth.controllers import router as auth_router
from src.apps.dummy.controllers import router as dummy_router
from src.apps.tasks.controllers import router as tasks_router
from src.apps.videos.controllers import router as videos_router

router: APIRouter = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(tasks_router, prefix="/tasks")
router.include_router(videos_router, prefix="/videos")
router.include_router(dummy_router, prefix="/dummy")

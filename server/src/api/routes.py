from fastapi import APIRouter

router = APIRouter()

# Include other routers

from .ui_routes import router as ui_router

# Mount the sub-routers

router.include_router(ui_router, prefix="/ui", tags=["User Interface"])
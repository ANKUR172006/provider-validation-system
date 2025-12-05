from fastapi import APIRouter
from .upload import router as upload_router
from .validation import router as validation_router
from .dashboard import router as dashboard_router
from .email import router as email_router

api_router = APIRouter()

api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(validation_router, prefix="/validation", tags=["validation"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(email_router, prefix="/email", tags=["email"])



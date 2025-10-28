from fastapi import APIRouter
from app.api.process_call_and_email import router as process_calls_routes


api_router = APIRouter()
api_router.include_router(process_calls_routes, prefix="/api/v1/process_calls", tags=["portfolio"])

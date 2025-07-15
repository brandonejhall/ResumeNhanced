"""
Health and info router
"""

from fastapi import APIRouter
from models import RootResponse
from config import settings

router = APIRouter(tags=["health"])

@router.get("/", response_model=RootResponse)
async def root():
    """Get API information"""
    return RootResponse(
        message=settings.APP_NAME,
        version=settings.APP_VERSION,
        endpoints={
            "POST /session/start": "Start a new resume analysis session",
            "POST /session/answer": "Submit an answer to the current question",
            "GET /session/{session_id}": "Get session status",
            "DELETE /session/{session_id}": "Delete a session"
        }
    )

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    } 
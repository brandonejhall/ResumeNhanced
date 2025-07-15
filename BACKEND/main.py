"""
AI Resume Assistant API - Main Application
"""

from fastapi import FastAPI
from config import settings
from routers import session_router, health_router

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered resume assistant that analyzes resumes against job postings",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(health_router.router)
app.include_router(session_router.router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    settings.validate()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    print("👋 Shutting down AI Resume Assistant API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
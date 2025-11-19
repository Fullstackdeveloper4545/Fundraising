from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import init_db
from app.api.v1.api import api_router
from app.core.exceptions import setup_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Fundraising Platform API",
    description="A comprehensive fundraising platform for high school students",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.get_trusted_hosts()
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Mount static files for uploads
import logging
logger = logging.getLogger(__name__)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("uploads/images", exist_ok=True)
os.makedirs("uploads/images/campaigns", exist_ok=True)

logger.info(f"Mounting static files from: {os.path.abspath('uploads')}")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Direct image serving endpoint as fallback
@app.get("/uploads/images/{category}/{filename}")
async def serve_image(category: str, filename: str):
    """Direct image serving endpoint"""
    file_path = f"uploads/images/{category}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Fundraising Platform API is running"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

"""
Static file serving endpoints for uploaded images
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Mount static files
router.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@router.get("/images/{category}/{filename}")
async def get_image(category: str, filename: str):
    """Get an uploaded image"""
    try:
        file_path = f"uploads/images/{category}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(
            file_path,
            media_type="image/jpeg",
            filename=filename
        )
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve image")

@router.get("/images/{category}/{filename}/thumbnails/{size}")
async def get_thumbnail(category: str, filename: str, size: str):
    """Get a thumbnail of an image"""
    try:
        # Parse size (e.g., "300x300")
        width, height = map(int, size.split('x'))
        
        base_name = os.path.splitext(filename)[0]
        thumb_filename = f"{base_name}_{width}x{height}.jpg"
        file_path = f"uploads/images/{category}/{thumb_filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        return FileResponse(
            file_path,
            media_type="image/jpeg",
            filename=thumb_filename
        )
    except Exception as e:
        logger.error(f"Error serving thumbnail: {e}")
        raise HTTPException(status_code=500, detail="Failed to serve thumbnail")

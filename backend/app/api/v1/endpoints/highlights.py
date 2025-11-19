from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import List, Optional
import logging

from app.core.database import get_supabase, get_supabase_admin
from app.core.auth import get_current_user
from app.models.user import User
from app.services.student_highlight_service import StudentHighlightService
from app.services.image_service import image_service
from app.core.exceptions import NotFoundException, ValidationException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/current")
async def get_current_highlighted_student():
    """Get the currently highlighted student"""
    try:
        # Use admin client to bypass RLS for public data access
        supabase = get_supabase_admin()
        highlight_service = StudentHighlightService(supabase)
        
        highlight = await highlight_service.get_current_highlighted_student()
        if not highlight:
            raise NotFoundException("No student currently highlighted")
        
        return highlight
    except Exception as e:
        logger.error(f"Error getting current highlighted student: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/donors")
async def get_highlighted_donors(limit: int = Query(10, le=50)):
    """Get list of highlighted donors"""
    try:
        # Use admin client to bypass RLS for public data access
        supabase = get_supabase_admin()
        highlight_service = StudentHighlightService(supabase)
        
        donors = await highlight_service.get_highlighted_donors(limit)
        return donors
    except Exception as e:
        logger.error(f"Error getting highlighted donors: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/weekly")
async def get_weekly_highlights():
    """Get weekly student highlights"""
    try:
        # Use admin client to bypass RLS for public data access
        supabase = get_supabase_admin()
        highlight_service = StudentHighlightService(supabase)
        
        highlights = await highlight_service.get_weekly_highlights()
        return highlights
    except Exception as e:
        logger.error(f"Error getting weekly highlights: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/student/{user_id}")
async def get_student_achievements(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get achievements for a specific student"""
    try:
        # Check if user is requesting their own achievements or is admin
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these achievements")
        
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        highlight_service = StudentHighlightService(supabase)
        
        achievements = await highlight_service.get_student_achievements(user_id)
        return achievements
    except Exception as e:
        logger.error(f"Error getting student achievements: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/create")
async def create_student_highlight(
    user_id: int = Form(...),
    achievement: str = Form(...),
    description: str = Form(...),
    image_url: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Create a new student highlight (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Handle image upload or URL
        final_image_url = image_url
        
        if image_file and image_file.filename:
            # Upload image file
            try:
                image_info = await image_service.upload_image(
                    image_file, 
                    category="highlights", 
                    user_id=user_id
                )
                final_image_url = image_info["url"]
                logger.info(f"Image uploaded for highlight: {final_image_url}")
            except Exception as e:
                logger.error(f"Failed to upload image: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to upload image: {str(e)}")
        
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        highlight_service = StudentHighlightService(supabase)
        
        result = await highlight_service.create_student_highlight(
            user_id, achievement, description, final_image_url
        )
        
        if not result:
            raise ValidationException("Failed to create student highlight")
        
        return {"message": "Student highlight created successfully"}
    except Exception as e:
        logger.error(f"Error creating student highlight: {e}")
        raise HTTPException(status_code=400, detail=str(e))

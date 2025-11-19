"""
Image upload and management service
"""

import os
import uuid
import shutil
from typing import Optional, Dict, Any
from fastapi import UploadFile, HTTPException
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageService:
    """Service for handling image uploads and processing"""
    
    def __init__(self):
        self.upload_dir = "uploads/images"
        self.allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.thumbnail_sizes = [(150, 150), (300, 300), (600, 600)]
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(f"{self.upload_dir}/thumbnails", exist_ok=True)
    
    async def upload_image(
        self, 
        file: UploadFile, 
        category: str = "general",
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Upload and process an image file
        
        Args:
            file: The uploaded file
            category: Category for organizing images (highlights, campaigns, etc.)
            user_id: ID of the user uploading the image
            
        Returns:
            Dict containing file info and URLs
        """
        try:
            # Validate file
            if not await self._validate_file(file):
                raise HTTPException(status_code=400, detail="Invalid file format or size")
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1].lower()
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Create category directory
            category_dir = f"{self.upload_dir}/{category}"
            os.makedirs(category_dir, exist_ok=True)
            
            # Save original file
            file_path = f"{category_dir}/{unique_filename}"
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Generate thumbnails
            thumbnails = await self._generate_thumbnails(file_path, category_dir, unique_filename)
            
            # Create file info
            file_info = {
                "original_filename": file.filename,
                "stored_filename": unique_filename,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "category": category,
                "user_id": user_id,
                "url": f"/uploads/images/{category}/{unique_filename}",
                "thumbnails": thumbnails
            }
            
            logger.info(f"Image uploaded successfully: {file_info['url']}")
            return file_info
            
        except Exception as e:
            logger.error(f"Error uploading image: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    async def _validate_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        try:
            # Check file size
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            if file_size > self.max_file_size:
                logger.warning(f"File too large: {file_size} bytes")
                return False
            
            # Check file extension
            if file.filename:
                file_extension = os.path.splitext(file.filename)[1].lower()
                if file_extension not in self.allowed_extensions:
                    logger.warning(f"Invalid file extension: {file_extension}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating file: {e}")
            return False
    
    async def _generate_thumbnails(self, original_path: str, category_dir: str, filename: str) -> Dict[str, str]:
        """Generate thumbnails of different sizes"""
        thumbnails = {}
        
        try:
            with Image.open(original_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                base_name = os.path.splitext(filename)[0]
                
                for size in self.thumbnail_sizes:
                    # Create thumbnail
                    thumbnail = img.copy()
                    thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Save thumbnail
                    thumb_filename = f"{base_name}_{size[0]}x{size[1]}.jpg"
                    thumb_path = f"{category_dir}/{thumb_filename}"
                    thumbnail.save(thumb_path, "JPEG", quality=85)
                    
                    thumbnails[f"{size[0]}x{size[1]}"] = f"/uploads/images/{os.path.basename(category_dir)}/{thumb_filename}"
                    
        except Exception as e:
            logger.error(f"Error generating thumbnails: {e}")
        
        return thumbnails
    
    async def delete_image(self, file_path: str) -> bool:
        """Delete an image and its thumbnails"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                
                # Delete thumbnails
                base_path = os.path.splitext(file_path)[0]
                for size in self.thumbnail_sizes:
                    thumb_path = f"{base_path}_{size[0]}x{size[1]}.jpg"
                    if os.path.exists(thumb_path):
                        os.remove(thumb_path)
                
                logger.info(f"Image deleted: {file_path}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error deleting image: {e}")
            return False
    
    def get_image_url(self, file_path: str) -> str:
        """Get the public URL for an image"""
        # Convert file path to URL
        if file_path.startswith(self.upload_dir):
            return file_path.replace(self.upload_dir, "/uploads/images")
        return file_path

# Global instance
image_service = ImageService()

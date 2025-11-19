"""
Comprehensive error handling utilities
"""

import logging
from typing import Any, Optional
from fastapi import HTTPException
from pydantic import ValidationError

logger = logging.getLogger(__name__)


def safe_get_attr(obj: Any, attr_name: str, default: Any = None) -> Any:
    """Safely get attribute from object with fallback"""
    try:
        return getattr(obj, attr_name, default)
    except AttributeError:
        logger.warning(f"Attribute {attr_name} not found on object {type(obj)}")
        return default


def safe_get_dict_key(dict_obj: dict, key: str, default: Any = None) -> Any:
    """Safely get key from dictionary with fallback"""
    try:
        return dict_obj.get(key, default)
    except (AttributeError, TypeError):
        logger.warning(f"Key {key} not found in dictionary")
        return default


def handle_validation_error(e: ValidationError) -> HTTPException:
    """Handle Pydantic validation errors"""
    error_details = []
    for error in e.errors():
        field = " -> ".join(str(x) for x in error["loc"])
        message = error["msg"]
        error_details.append(f"{field}: {message}")
    
    return HTTPException(
        status_code=422,
        detail={
            "error": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "details": error_details
        }
    )


def handle_attribute_error(e: AttributeError) -> HTTPException:
    """Handle attribute errors"""
    logger.error(f"Attribute error: {e}")
    return HTTPException(
        status_code=500,
        detail={
            "error": "Internal server error - missing attribute",
            "error_code": "ATTRIBUTE_ERROR",
            "message": str(e)
        }
    )


def handle_database_error(e: Exception) -> HTTPException:
    """Handle database errors"""
    logger.error(f"Database error: {e}")
    return HTTPException(
        status_code=500,
        detail={
            "error": "Database operation failed",
            "error_code": "DATABASE_ERROR",
            "message": "Please try again later"
        }
    )


def create_safe_user_response(user: Any) -> dict:
    """Create a safe user response that won't fail on missing attributes"""
    return {
        "id": safe_get_attr(user, "id"),
        "email": safe_get_attr(user, "email"),
        "first_name": safe_get_attr(user, "first_name"),
        "last_name": safe_get_attr(user, "last_name"),
        "phone": safe_get_attr(user, "phone"),
        "role": safe_get_attr(user, "role"),
        "status": safe_get_attr(user, "status"),
        "is_verified": safe_get_attr(user, "is_verified", False),
        "created_at": safe_get_attr(user, "created_at")
    }

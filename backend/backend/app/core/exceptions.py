from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class ValidationException(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail, error_code="VALIDATION_ERROR")


class AuthenticationException(CustomHTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail, error_code="AUTH_ERROR")


class AuthorizationException(CustomHTTPException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status_code=403, detail=detail, error_code="AUTHORIZATION_ERROR")


class NotFoundException(CustomHTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")


class PaymentException(CustomHTTPException):
    def __init__(self, detail: str = "Payment processing failed"):
        super().__init__(status_code=402, detail=detail, error_code="PAYMENT_ERROR")


class CampaignException(CustomHTTPException):
    def __init__(self, detail: str = "Campaign operation failed"):
        super().__init__(status_code=400, detail=detail, error_code="CAMPAIGN_ERROR")


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_code": exc.error_code,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation error",
                "error_code": "VALIDATION_ERROR",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "error_code": "HTTP_ERROR",
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "error_code": "INTERNAL_ERROR",
                "status_code": 500
            }
        )

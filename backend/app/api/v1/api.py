from fastapi import APIRouter
from app.api.v1.endpoints import auth, campaigns, payments, referrals, shoutouts, milestones, receipts, companies, admin, highlights, email_test, otp_verification, partnership, static

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(payments.router, prefix="/payments", tags=["payments"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(shoutouts.router, prefix="/shoutouts", tags=["shoutouts"])
api_router.include_router(milestones.router, prefix="/milestones", tags=["milestones"])
api_router.include_router(receipts.router, prefix="/receipts", tags=["receipts"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(highlights.router, prefix="/highlights", tags=["highlights"])
api_router.include_router(email_test.router, prefix="/email-test", tags=["email-testing"])
api_router.include_router(otp_verification.router, prefix="/otp", tags=["otp-verification"])
api_router.include_router(partnership.router, prefix="/partnership", tags=["partnership"])
api_router.include_router(static.router, prefix="/static", tags=["static-files"])
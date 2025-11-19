from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.core.database import get_supabase, get_supabase_admin
from app.core.auth import get_current_user
from app.models.user import User
from app.models.campaign import CampaignStatus
from app.services.admin_service import AdminService
from app.core.exceptions import AuthorizationException

router = APIRouter()
logger = logging.getLogger(__name__)


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is admin"""
    if current_user.role != "admin":
        raise AuthorizationException("Admin access required")
    return current_user


@router.get("/stats")
async def get_platform_stats(admin_user: User = Depends(get_admin_user)):
    """Get platform statistics"""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        stats = await admin_service.get_platform_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting platform stats: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/campaigns")
async def get_all_campaigns(admin_user: User = Depends(get_admin_user)):
    """Get all campaigns for admin"""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        campaigns = await admin_service.get_all_campaigns()
        return campaigns
    except Exception as e:
        logger.error(f"Error getting all campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/feature")
async def feature_campaign(
    campaign_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Feature a campaign"""
    try:
        # Use admin client to avoid RLS limitations on listing
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.feature_campaign(campaign_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to feature campaign")
        
        return {"message": "Campaign featured successfully"}
    except Exception as e:
        logger.error(f"Error featuring campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/close")
async def close_campaign(
    campaign_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Permanently close a campaign."""
    try:
        # Use admin client to bypass RLS for admin operations
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)

        result = await admin_service.close_campaign_permanently(campaign_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to close campaign")

        return {"message": "Campaign closed permanently"}
    except Exception as e:
        logger.error(f"Error closing campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/campaigns/{campaign_id}/status/{status}")
async def set_campaign_status(
    campaign_id: int,
    status: CampaignStatus,
    admin_user: User = Depends(get_admin_user)
):
    """Set campaign status to any valid `CampaignStatus` value."""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)

        ok = await admin_service.update_campaign_status(campaign_id, status.value)
        if not ok:
            raise HTTPException(status_code=400, detail="Failed to update status")
        return {"message": f"Campaign status set to {status.value}"}
    except Exception as e:
        logger.error(f"Error setting campaign status: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/users")
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    """Get all users for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        users = await admin_service.get_all_users()
        return users
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===== COMPREHENSIVE ADMIN CRUD ENDPOINTS =====

# User Management
@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    user_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any user (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_user(user_id, user_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update user")
        
        return {"message": "User updated successfully"}
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any user (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_user(user_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete user")
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Campaign Management
@router.put("/campaigns/{campaign_id}")
async def admin_update_campaign(
    campaign_id: int,
    campaign_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any campaign (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_campaign(campaign_id, campaign_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update campaign")
        
        return {"message": "Campaign updated successfully"}
    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/campaigns/{campaign_id}")
async def admin_delete_campaign(
    campaign_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any campaign (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_campaign(campaign_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete campaign")
        
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Payment Management
@router.get("/payments")
async def get_all_payments(admin_user: User = Depends(get_admin_user)):
    """Get all payments for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        payments = await admin_service.get_all_payments()
        return payments
    except Exception as e:
        logger.error(f"Error getting all payments: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/payments/{payment_id}")
async def admin_update_payment(
    payment_id: int,
    payment_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any payment (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_payment(payment_id, payment_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update payment")
        
        return {"message": "Payment updated successfully"}
    except Exception as e:
        logger.error(f"Error updating payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/payments/{payment_id}")
async def admin_delete_payment(
    payment_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any payment (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_payment(payment_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete payment")
        
        return {"message": "Payment deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting payment: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Company Management
@router.put("/companies/{company_id}")
async def admin_update_company(
    company_id: int,
    company_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any company (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_company(company_id, company_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update company")
        
        return {"message": "Company updated successfully"}
    except Exception as e:
        logger.error(f"Error updating company: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/companies/{company_id}")
async def admin_delete_company(
    company_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any company (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_company(company_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete company")
        
        return {"message": "Company deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting company: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Milestone Management
@router.get("/milestones")
async def get_all_milestones(admin_user: User = Depends(get_admin_user)):
    """Get all milestones for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        milestones = await admin_service.get_all_milestones()
        return milestones
    except Exception as e:
        logger.error(f"Error getting all milestones: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/milestones/{milestone_id}")
async def admin_update_milestone(
    milestone_id: int,
    milestone_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any milestone (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_milestone(milestone_id, milestone_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update milestone")
        
        return {"message": "Milestone updated successfully"}
    except Exception as e:
        logger.error(f"Error updating milestone: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/milestones/{milestone_id}")
async def admin_delete_milestone(
    milestone_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any milestone (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_milestone(milestone_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete milestone")
        
        return {"message": "Milestone deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting milestone: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Receipt Management
@router.get("/receipts")
async def get_all_receipts(admin_user: User = Depends(get_admin_user)):
    """Get all receipts for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        receipts = await admin_service.get_all_receipts()
        return receipts
    except Exception as e:
        logger.error(f"Error getting all receipts: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/receipts/{receipt_id}")
async def admin_delete_receipt(
    receipt_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any receipt (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_receipt(receipt_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete receipt")
        
        return {"message": "Receipt deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting receipt: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Referral Management
@router.get("/referrals")
async def get_all_referrals(admin_user: User = Depends(get_admin_user)):
    """Get all referrals for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        referrals = await admin_service.get_all_referrals()
        return referrals
    except Exception as e:
        logger.error(f"Error getting all referrals: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/referrals/{referral_id}")
async def admin_update_referral(
    referral_id: int,
    referral_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any referral (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_referral(referral_id, referral_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update referral")
        
        return {"message": "Referral updated successfully"}
    except Exception as e:
        logger.error(f"Error updating referral: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/referrals/{referral_id}")
async def admin_delete_referral(
    referral_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any referral (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_referral(referral_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete referral")
        
        return {"message": "Referral deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting referral: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Shoutout Management
@router.get("/shoutouts")
async def get_all_shoutouts(admin_user: User = Depends(get_admin_user)):
    """Get all shoutouts for admin"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        shoutouts = await admin_service.get_all_shoutouts()
        return shoutouts
    except Exception as e:
        logger.error(f"Error getting all shoutouts: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/shoutouts/{shoutout_id}")
async def admin_update_shoutout(
    shoutout_id: int,
    shoutout_data: dict,
    admin_user: User = Depends(get_admin_user)
):
    """Update any shoutout (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.update_shoutout(shoutout_id, shoutout_data)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to update shoutout")
        
        return {"message": "Shoutout updated successfully"}
    except Exception as e:
        logger.error(f"Error updating shoutout: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/shoutouts/{shoutout_id}")
async def admin_delete_shoutout(
    shoutout_id: int,
    admin_user: User = Depends(get_admin_user)
):
    """Delete any shoutout (admin only)"""
    try:
        supabase = get_supabase_admin()
        admin_service = AdminService(supabase)
        
        result = await admin_service.delete_shoutout(shoutout_id)
        if not result:
            raise HTTPException(status_code=400, detail="Failed to delete shoutout")
        
        return {"message": "Shoutout deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting shoutout: {e}")
        raise HTTPException(status_code=400, detail=str(e))

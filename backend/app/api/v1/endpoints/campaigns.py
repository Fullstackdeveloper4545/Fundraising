from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_supabase, get_supabase_admin
from app.services.user_service import UserService
from app.models.user import UserCreate, UserRole
import secrets
from app.core.auth import get_current_user
from app.models.user import User
from app.models.campaign import Campaign, CampaignCreate, CampaignUpdate, CampaignResponse, CampaignStatus
from app.services.campaign_service import CampaignService
from app.services.image_service import image_service
from app.core.exceptions import NotFoundException, ValidationException, CampaignException

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CampaignResponse)
async def create_campaign(
    campaign_data: CampaignCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign"""
    try:
        # Use admin client to bypass RLS for controlled server-side insert
        supabase = get_supabase_admin()
        campaign_service = CampaignService(supabase)
        user_service = UserService(supabase)
        
        # Allow only students and admins to create campaigns
        if current_user.role not in ("student", "admin"):
            raise CampaignException("Only student and admin roles can create campaigns")

        # Students can create campaigns in draft status without referral requirements
        # Campaigns will be promoted to pending_approval after 5 referrals are accepted
        
        # Determine effective user_id (admin special-case uses a real DB user)
        effective_user_id = current_user.id
        if effective_user_id == -1:
            # Map virtual admin to a real user row
            admin_user = await user_service.get_user_by_email(current_user.email)
            if not admin_user:
                # Create admin user with a strong random password
                random_password = secrets.token_urlsafe(24)
                created_admin = await user_service.create_user(UserCreate(
                    email=current_user.email,
                    password=random_password,
                    first_name=current_user.first_name or "Admin",
                    last_name=current_user.last_name or "User",
                    role=UserRole.ADMIN
                ))
                effective_user_id = created_admin.id  # type: ignore
            else:
                effective_user_id = admin_user.id  # type: ignore

        # Create campaign
        campaign = await campaign_service.create_campaign(int(effective_user_id), campaign_data)
        
        # Send campaign creation notification email
        try:
            from app.services.email_service import EmailService
            email_service = EmailService()
            user_name = f"{current_user.first_name} {current_user.last_name}"
            
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #4F46E5;">📝 Campaign Created in Draft Status!</h2>
                    <p>Hello {user_name},</p>
                    <p>Your fundraising campaign has been created and is currently in draft status.</p>
                    <p><strong>Campaign Details:</strong></p>
                    <ul>
                        <li>Title: {campaign.title}</li>
                        <li>Goal: ${campaign.goal_amount}</li>
                        <li>Duration: {campaign.duration_months} months</li>
                        <li>Status: {campaign.status.title()}</li>
                        <li>Created: {campaign.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC</li>
                    </ul>
                    <p><strong>Next Steps:</strong></p>
                    <ol>
                        <li><strong>Refer 5 friends</strong> to get your campaign approved</li>
                        <li>Share your referral links with friends and family</li>
                        <li>Use social media to spread the word</li>
                        <li>Once 5 referrals are accepted, your campaign will go to admin for approval</li>
                    </ol>
                    <p>Your campaign will become active after admin approval!</p>
                    <hr style="margin: 30px 0; border: none; border-top: 1px solid #dee2e6;">
                    <p style="color: #6c757d; font-size: 14px;">
                        Best regards,<br>
                        The Fundraising Platform Team
                    </p>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Campaign Created in Draft Status!
            
            Hello {user_name},
            
            Your fundraising campaign has been created and is currently in draft status.
            
            Campaign Details:
            - Title: {campaign.title}
            - Goal: ${campaign.goal_amount}
            - Duration: {campaign.duration_months} months
            - Status: {campaign.status.title()}
            - Created: {campaign.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            Next Steps:
            1. Refer 5 friends to get your campaign approved
            2. Share your referral links with friends and family
            3. Use social media to spread the word
            4. Once 5 referrals are accepted, your campaign will go to admin for approval
            
            Your campaign will become active after admin approval!
            
            Best regards,
            The Fundraising Platform Team
            """
            
            await email_service.send_email(
                current_user.email,
                "📝 Campaign Created in Draft Status - Fundraising Platform",
                html_content,
                text_content
            )
            logger.info(f"Campaign creation notification email sent to {current_user.email}")
        except Exception as email_error:
            logger.warning(f"Failed to send campaign creation notification email to {current_user.email}: {email_error}")
            # Don't fail campaign creation if email fails
        
        return CampaignResponse(
            id=campaign.id,
            user_id=campaign.user_id,
            title=campaign.title,
            description=campaign.description,
            goal_amount=campaign.goal_amount,
            current_amount=campaign.current_amount,
            status=campaign.status,
            duration_months=campaign.duration_months,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            category=campaign.category,
            image_url=campaign.image_url,
            video_url=campaign.video_url,
            story=campaign.story,
            is_featured=campaign.is_featured,
            referral_requirement_met=campaign.referral_requirement_met,
            referral_count=campaign.referral_count or 0,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
            days_remaining=await campaign_service.calculate_days_remaining(campaign),
            donor_count=await campaign_service.get_donor_count(campaign.id)
        )
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/with-image", response_model=CampaignResponse)
async def create_campaign_with_image(
    title: str = Form(...),
    description: str = Form(...),
    goal_amount: float = Form(...),
    duration_months: str = Form(...),
    category: Optional[str] = Form(None),
    story: Optional[str] = Form(None),
    video_url: Optional[str] = Form(None),
    image_url: Optional[str] = Form(None),
    image_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user)
):
    """Create a new campaign with image upload support"""
    try:
        # Handle image upload or URL
        final_image_url = image_url
        
        if image_file and image_file.filename:
            # Upload image file
            try:
                image_info = await image_service.upload_image(
                    image_file, 
                    category="campaigns", 
                    user_id=current_user.id
                )
                final_image_url = image_info["url"]
                logger.info(f"Image uploaded for campaign: {final_image_url}")
            except Exception as e:
                logger.error(f"Failed to upload image: {e}")
                raise HTTPException(status_code=400, detail=f"Failed to upload image: {str(e)}")
        
        # Create campaign data
        campaign_data = CampaignCreate(
            title=title,
            description=description,
            goal_amount=goal_amount,
            duration_months=duration_months,
            category=category,
            story=story,
            video_url=video_url,
            image_url=final_image_url
        )
        
        # Use admin client to bypass RLS for controlled server-side insert
        supabase = get_supabase_admin()
        campaign_service = CampaignService(supabase)
        user_service = UserService(supabase)
        
        # Allow only students and admins to create campaigns
        if current_user.role not in ("student", "admin"):
            raise CampaignException("Only student and admin roles can create campaigns")

        # Students can create campaigns in draft status without referral requirements
        # Campaigns will be promoted to pending_approval after 5 referrals are accepted

        # Determine effective user_id (admin special-case uses a real DB user)
        effective_user_id = current_user.id
        if effective_user_id == -1:
            admin_user = await user_service.get_user_by_email(current_user.email)
            if not admin_user:
                random_password = secrets.token_urlsafe(24)
                created_admin = await user_service.create_user(UserCreate(
                    email=current_user.email,
                    password=random_password,
                    first_name=current_user.first_name or "Admin",
                    last_name=current_user.last_name or "User",
                    role=UserRole.ADMIN
                ))
                effective_user_id = created_admin.id  # type: ignore
            else:
                effective_user_id = admin_user.id  # type: ignore

        # Create campaign
        campaign = await campaign_service.create_campaign(int(effective_user_id), campaign_data)
        
        return CampaignResponse(
            id=campaign.id,
            user_id=campaign.user_id,
            title=campaign.title,
            description=campaign.description,
            goal_amount=campaign.goal_amount,
            current_amount=campaign.current_amount,
            status=campaign.status,
            duration_months=campaign.duration_months,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            category=campaign.category,
            image_url=campaign.image_url,
            video_url=campaign.video_url,
            story=campaign.story,
            is_featured=campaign.is_featured,
            referral_requirement_met=campaign.referral_requirement_met,
            referral_count=campaign.referral_count or 0,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
            days_remaining=await campaign_service.calculate_days_remaining(campaign),
            donor_count=await campaign_service.get_donor_count(campaign.id)
        )
    except Exception as e:
        logger.error(f"Error creating campaign with image: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CampaignResponse])
async def get_campaigns(
    status: Optional[CampaignStatus] = None,
    category: Optional[str] = None,
    featured: Optional[bool] = None,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0)
):
    """Get all campaigns with optional filters"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        campaigns = await campaign_service.get_campaigns(
            status=status,
            category=category,
            featured=featured,
            limit=limit,
            offset=offset
        )
        
        campaign_responses = []
        for campaign in campaigns:
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                user_id=campaign.user_id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=campaign.goal_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                duration_months=campaign.duration_months,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                category=campaign.category,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                story=campaign.story,
                is_featured=campaign.is_featured,
                referral_requirement_met=campaign.referral_requirement_met,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
                days_remaining=await campaign_service.calculate_days_remaining(campaign),
                donor_count=await campaign_service.get_donor_count(campaign.id)
            ))
        
        return campaign_responses
    except Exception as e:
        logger.error(f"Error getting campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/featured", response_model=List[CampaignResponse])
async def get_featured_campaigns(
    limit: int = Query(10, le=20)
):
    """Get featured campaigns"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        campaigns = await campaign_service.get_campaigns(
            status=CampaignStatus.ACTIVE,
            featured=True,
            limit=limit
        )
        
        campaign_responses = []
        for campaign in campaigns:
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                user_id=campaign.user_id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=campaign.goal_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                duration_months=campaign.duration_months,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                category=campaign.category,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                story=campaign.story,
                is_featured=campaign.is_featured,
                referral_requirement_met=campaign.referral_requirement_met,
                referral_count=campaign.referral_count or 0,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
                days_remaining=await campaign_service.calculate_days_remaining(campaign),
                donor_count=await campaign_service.get_donor_count(campaign.id)
            ))
        
        return campaign_responses
    except Exception as e:
        logger.error(f"Error getting featured campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/spotlight", response_model=List[CampaignResponse])
async def get_spotlight_campaigns(
    limit: int = Query(6, le=12)
):
    """Get spotlight campaigns - top performing campaigns"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Get active campaigns and sort by progress percentage
        campaigns = await campaign_service.get_campaigns(
            status=CampaignStatus.ACTIVE,
            limit=limit * 2  # Get more to filter by performance
        )
        
        # Sort by progress percentage (highest first)
        campaigns.sort(key=lambda x: x.current_amount / x.goal_amount if x.goal_amount > 0 else 0, reverse=True)
        
        # Take top performers
        top_campaigns = campaigns[:limit]
        
        campaign_responses = []
        for campaign in top_campaigns:
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                user_id=campaign.user_id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=campaign.goal_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                duration_months=campaign.duration_months,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                category=campaign.category,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                story=campaign.story,
                is_featured=campaign.is_featured,
                referral_requirement_met=campaign.referral_requirement_met,
                referral_count=campaign.referral_count or 0,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
                days_remaining=await campaign_service.calculate_days_remaining(campaign),
                donor_count=await campaign_service.get_donor_count(campaign.id)
            ))
        
        return campaign_responses
    except Exception as e:
        logger.error(f"Error getting spotlight campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(campaign_id: int):
    """Get a specific campaign by ID"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        campaign = await campaign_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise NotFoundException("Campaign not found")
        
        return CampaignResponse(
            id=campaign.id,
            user_id=campaign.user_id,
            title=campaign.title,
            description=campaign.description,
            goal_amount=campaign.goal_amount,
            current_amount=campaign.current_amount,
            status=campaign.status,
            duration_months=campaign.duration_months,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            category=campaign.category,
            image_url=campaign.image_url,
            video_url=campaign.video_url,
            story=campaign.story,
            is_featured=campaign.is_featured,
            referral_requirement_met=campaign.referral_requirement_met,
            referral_count=campaign.referral_count or 0,
            created_at=campaign.created_at,
            updated_at=campaign.updated_at,
            progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
            days_remaining=await campaign_service.calculate_days_remaining(campaign),
            donor_count=await campaign_service.get_donor_count(campaign.id)
        )
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    campaign_data: CampaignUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update a campaign"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Check if user owns the campaign or is admin
        campaign = await campaign_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise NotFoundException("Campaign not found")
        
        if campaign.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to update this campaign")
        
        # Update campaign
        updated_campaign = await campaign_service.update_campaign(campaign_id, campaign_data)
        
        return CampaignResponse(
            id=updated_campaign.id,
            user_id=updated_campaign.user_id,
            title=updated_campaign.title,
            description=updated_campaign.description,
            goal_amount=updated_campaign.goal_amount,
            current_amount=updated_campaign.current_amount,
            status=updated_campaign.status,
            duration_months=updated_campaign.duration_months,
            start_date=updated_campaign.start_date,
            end_date=updated_campaign.end_date,
            category=updated_campaign.category,
            image_url=updated_campaign.image_url,
            video_url=updated_campaign.video_url,
            story=updated_campaign.story,
            is_featured=updated_campaign.is_featured,
            referral_requirement_met=updated_campaign.referral_requirement_met,
            created_at=updated_campaign.created_at,
            updated_at=updated_campaign.updated_at,
            progress_percentage=float(updated_campaign.current_amount / updated_campaign.goal_amount * 100),
            days_remaining=await campaign_service.calculate_days_remaining(updated_campaign),
            donor_count=await campaign_service.get_donor_count(updated_campaign.id)
        )
    except Exception as e:
        logger.error(f"Error updating campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{campaign_id}")
async def delete_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user)
):
    """Delete a campaign"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Check if user owns the campaign or is admin
        campaign = await campaign_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise NotFoundException("Campaign not found")
        
        if campaign.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to delete this campaign")
        
        # Delete campaign
        await campaign_service.delete_campaign(campaign_id)
        
        return {"message": "Campaign deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user)
):
    """Start a campaign"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Check if user owns the campaign or is admin
        campaign = await campaign_service.get_campaign_by_id(campaign_id)
        if not campaign:
            raise NotFoundException("Campaign not found")
        
        if campaign.user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to start this campaign")
        
        # Start campaign
        await campaign_service.start_campaign(campaign_id)
        
        return {"message": "Campaign started successfully"}
    except Exception as e:
        logger.error(f"Error starting campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user/{user_id}", response_model=List[CampaignResponse])
async def get_user_campaigns(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get campaigns for a specific user"""
    try:
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Check if user is requesting their own campaigns or is admin
        if user_id != current_user.id and current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to view these campaigns")
        
        campaigns = await campaign_service.get_user_campaigns(user_id)
        
        campaign_responses = []
        for campaign in campaigns:
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                user_id=campaign.user_id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=campaign.goal_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                duration_months=campaign.duration_months,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                category=campaign.category,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                story=campaign.story,
                is_featured=campaign.is_featured,
                referral_requirement_met=campaign.referral_requirement_met,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
                days_remaining=await campaign_service.calculate_days_remaining(campaign),
                donor_count=await campaign_service.get_donor_count(campaign.id)
            ))
        
        return campaign_responses
    except Exception as e:
        logger.error(f"Error getting user campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/pending-approval", response_model=List[CampaignResponse])
async def get_pending_approval_campaigns(
    current_user: User = Depends(get_current_user)
):
    """Get campaigns pending admin approval (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        campaigns = await campaign_service.get_pending_approval_campaigns()
        
        campaign_responses = []
        for campaign in campaigns:
            campaign_responses.append(CampaignResponse(
                id=campaign.id,
                user_id=campaign.user_id,
                title=campaign.title,
                description=campaign.description,
                goal_amount=campaign.goal_amount,
                current_amount=campaign.current_amount,
                status=campaign.status,
                duration_months=campaign.duration_months,
                start_date=campaign.start_date,
                end_date=campaign.end_date,
                category=campaign.category,
                image_url=campaign.image_url,
                video_url=campaign.video_url,
                story=campaign.story,
                is_featured=campaign.is_featured,
                referral_requirement_met=campaign.referral_requirement_met,
                referral_count=campaign.referral_count,
                created_at=campaign.created_at,
                updated_at=campaign.updated_at,
                progress_percentage=float(campaign.current_amount / campaign.goal_amount * 100),
                days_remaining=await campaign_service.calculate_days_remaining(campaign),
                donor_count=await campaign_service.get_donor_count(campaign.id)
            ))
        
        return campaign_responses
    except Exception as e:
        logger.error(f"Error getting pending approval campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{campaign_id}/approve")
async def approve_campaign(
    campaign_id: int,
    current_user: User = Depends(get_current_user)
):
    """Approve a campaign (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        supabase = get_supabase()
        campaign_service = CampaignService(supabase)
        
        # Approve campaign
        success = await campaign_service.approve_campaign(campaign_id)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to approve campaign")
        
        return {"message": "Campaign approved successfully"}
    except Exception as e:
        logger.error(f"Error approving campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))

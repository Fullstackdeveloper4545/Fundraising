# Admin Privileges Summary

This document outlines all the comprehensive CRUD (Create, Read, Update, Delete) privileges that have been granted to Admin users in the fundraising platform.

## Overview

Admin users now have **full control** over all entities in the system. They can:
- Create, read, update, and delete any record
- Bypass all ownership restrictions
- Access all data regardless of user permissions
- Manage the entire platform

## Admin Authentication

Admin users are identified by:
- Role: `"admin"`
- Special config admin with ID `-1` (configured via environment variables)
- Regular admin users in the database with `role = "admin"`

## Comprehensive Admin Privileges

### 1. User Management
**Endpoint:** `/api/v1/admin/users`

#### Read Operations:
- `GET /admin/users` - Get all users in the system
- `GET /admin/users/{user_id}` - Get any specific user

#### Create Operations:
- `POST /api/v1/auth/admin/create-user` - Create users with any role (admin, student, company, donor)

#### Update Operations:
- `PUT /admin/users/{user_id}` - Update any user's information

#### Delete Operations:
- `DELETE /admin/users/{user_id}` - Delete any user from the system

### 2. Campaign Management
**Endpoint:** `/api/v1/admin/campaigns`

#### Read Operations:
- `GET /admin/campaigns` - Get all campaigns in the system
- `GET /admin/campaigns/{campaign_id}` - Get any specific campaign

#### Update Operations:
- `PUT /admin/campaigns/{campaign_id}` - Update any campaign
- `POST /admin/campaigns/{campaign_id}/feature` - Feature/unfeature campaigns
- `POST /admin/campaigns/{campaign_id}/close` - Close campaigns permanently
- `POST /admin/campaigns/{campaign_id}/status/{status}` - Set campaign status

#### Delete Operations:
- `DELETE /admin/campaigns/{campaign_id}` - Delete any campaign

#### Regular Endpoint Access:
- `PUT /api/v1/campaigns/{campaign_id}` - Update any campaign (bypasses ownership check)
- `DELETE /api/v1/campaigns/{campaign_id}` - Delete any campaign (bypasses ownership check)
- `POST /api/v1/campaigns/{campaign_id}/start` - Start any campaign (bypasses ownership check)

### 3. Payment Management
**Endpoint:** `/api/v1/admin/payments`

#### Read Operations:
- `GET /admin/payments` - Get all payments in the system
- `GET /admin/payments/{payment_id}` - Get any specific payment

#### Create Operations:
- `POST /api/v1/payments/` - Create payments (admin can create payments for any campaign)

#### Update Operations:
- `PUT /admin/payments/{payment_id}` - Update any payment
- `POST /api/v1/payments/{payment_id}/process` - Process any payment

#### Delete Operations:
- `DELETE /admin/payments/{payment_id}` - Delete any payment

#### Regular Endpoint Access:
- `POST /api/v1/payments/{payment_id}/refund` - Refund any payment (bypasses ownership check)

### 4. Company Management
**Endpoint:** `/api/v1/admin/companies`

#### Read Operations:
- `GET /api/v1/companies/` - Get all companies

#### Create Operations:
- `POST /api/v1/companies/` - Create companies (admin only)

#### Update Operations:
- `PUT /admin/companies/{company_id}` - Update any company

#### Delete Operations:
- `DELETE /admin/companies/{company_id}` - Delete any company

### 5. Milestone Management
**Endpoint:** `/api/v1/admin/milestones`

#### Read Operations:
- `GET /admin/milestones` - Get all milestones in the system

#### Create Operations:
- `POST /api/v1/milestones/` - Create milestones (admin can create for any campaign)

#### Update Operations:
- `PUT /admin/milestones/{milestone_id}` - Update any milestone

#### Delete Operations:
- `DELETE /admin/milestones/{milestone_id}` - Delete any milestone

### 6. Receipt Management
**Endpoint:** `/api/v1/admin/receipts`

#### Read Operations:
- `GET /admin/receipts` - Get all receipts in the system
- `GET /api/v1/receipts/payment/{payment_id}` - Get any receipt

#### Delete Operations:
- `DELETE /admin/receipts/{receipt_id}` - Delete any receipt

#### Regular Endpoint Access:
- `GET /api/v1/receipts/user/{user_id}` - Get any user's receipts (bypasses ownership check)

### 7. Referral Management
**Endpoint:** `/api/v1/admin/referrals`

#### Read Operations:
- `GET /admin/referrals` - Get all referrals in the system

#### Create Operations:
- `POST /api/v1/referrals/` - Create referrals (admin can create for any campaign)

#### Update Operations:
- `PUT /admin/referrals/{referral_id}` - Update any referral

#### Delete Operations:
- `DELETE /admin/referrals/{referral_id}` - Delete any referral

#### Regular Endpoint Access:
- `GET /api/v1/referrals/campaign/{campaign_id}` - Get any campaign's referrals (bypasses ownership check)
- `GET /api/v1/referrals/stats/{campaign_id}` - Get any campaign's referral stats (bypasses ownership check)

### 8. Shoutout Management
**Endpoint:** `/api/v1/admin/shoutouts`

#### Read Operations:
- `GET /admin/shoutouts` - Get all shoutouts in the system

#### Create Operations:
- `POST /api/v1/shoutouts/` - Create shoutouts (admin can create for any campaign)

#### Update Operations:
- `PUT /admin/shoutouts/{shoutout_id}` - Update any shoutout

#### Delete Operations:
- `DELETE /admin/shoutouts/{shoutout_id}` - Delete any shoutout

### 9. Platform Statistics
**Endpoint:** `/api/v1/admin/stats`

#### Read Operations:
- `GET /admin/stats` - Get comprehensive platform statistics

## Key Features of Admin Privileges

### 1. Bypass Ownership Restrictions
- Admins can access, modify, and delete any record regardless of who created it
- No "ownership" checks apply to admin users
- Admins can act on behalf of any user

### 2. Full Database Access
- All admin operations use `get_supabase_admin()` to bypass Row Level Security (RLS)
- Admins can see all data in the system
- No data is hidden from admin users

### 3. Role Flexibility
- Admins can create users with any role (admin, student, company, donor)
- Admins can modify user roles and permissions
- Admins can suspend or activate any user account

### 4. Campaign Control
- Admins can create, modify, and delete any campaign
- Admins can change campaign status, feature campaigns, and close them
- Admins can bypass referral requirements for campaign creation

### 5. Payment Management
- Admins can process, refund, and modify any payment
- Admins can create payments on behalf of any donor
- Admins have full access to payment history and receipts

### 6. System Administration
- Admins can manage all platform entities
- Admins can view comprehensive statistics
- Admins can perform bulk operations

## Security Considerations

1. **Admin Authentication**: All admin endpoints require valid admin authentication
2. **Role Verification**: Every admin operation verifies the user has `role = "admin"`
3. **Audit Trail**: All admin operations are logged for security auditing
4. **Database Security**: Admin operations use admin-level database access

## Usage Examples

### Creating a User as Admin
```bash
POST /api/v1/auth/admin/create-user
Authorization: Bearer <admin_token>
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "role": "student"
}
```

### Updating Any Campaign
```bash
PUT /api/v1/admin/campaigns/123
Authorization: Bearer <admin_token>
{
  "title": "Updated Campaign Title",
  "goal_amount": 5000.00,
  "status": "active"
}
```

### Deleting Any Payment
```bash
DELETE /api/v1/admin/payments/456
Authorization: Bearer <admin_token>
```

## Conclusion

The admin user now has **complete control** over the entire fundraising platform. They can perform any CRUD operation on any entity, bypass all ownership restrictions, and manage the system comprehensively. This provides the necessary administrative capabilities for platform management while maintaining security through proper authentication and authorization checks.


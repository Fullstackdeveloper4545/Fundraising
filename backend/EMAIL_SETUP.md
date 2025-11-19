# 📧 Email Service Setup Guide

## Quick Fix for Email Issues

The email service is designed to work in two modes:

### 🔧 **Development Mode (No Email Configuration)**
- Emails are logged to console instead of being sent
- Perfect for development and testing
- No SMTP configuration needed

### 📧 **Production Mode (Full Email Configuration)**
- Requires SMTP server configuration
- Sends actual emails to users

## 🚀 **Quick Start (Development)**

For development, you don't need to configure email. The service will automatically log emails to the console.

```bash
# Test email service
python test_email.py

# Start your server
python start_dev.py
```

## 📧 **Production Email Setup**

### Option 1: Gmail SMTP (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Update your `.env` file**:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
```

### Option 2: Other SMTP Providers

```env
# For other providers, update these values:
SMTP_HOST=your-smtp-host.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
EMAIL_FROM=your-email@domain.com
```

## 🧪 **Testing Email Service**

```bash
# Test email functionality
python test_email.py

# Check email logs in your server output
python start_dev.py
```

## 📋 **Email Features**

The platform sends these types of emails:

- ✅ **Welcome Email**: New user registration
- ✅ **Referral Email**: Invitation to support campaigns
- ✅ **Donation Confirmation**: Thank you for donations
- ✅ **Campaign Updates**: Progress notifications
- ✅ **Password Reset**: Account recovery

## 🔍 **Debugging Email Issues**

### Check Configuration
```bash
python test_email.py
```

### Check Logs
Look for these log messages:
- `Email not configured, logging email instead` - Development mode
- `Email sent successfully` - Production mode working
- `Failed to send email` - Production mode with errors

### Common Issues

1. **"Email not configured"**
   - **Solution**: This is normal for development
   - **Fix**: Configure SMTP in `.env` for production

2. **"SMTP authentication failed"**
   - **Solution**: Check username/password
   - **Fix**: Use app password for Gmail

3. **"Connection timeout"**
   - **Solution**: Check SMTP host and port
   - **Fix**: Verify network connectivity

## 🎯 **Email Templates**

The service includes these email templates:

- **Welcome Email**: Introduces new users to the platform
- **Referral Email**: Invites friends to support campaigns
- **Donation Confirmation**: Thanks donors for their support
- **Campaign Updates**: Notifies supporters of progress
- **Password Reset**: Helps users recover accounts

## 🚀 **Production Deployment**

1. **Configure SMTP** in your production environment
2. **Set environment variables** for your SMTP provider
3. **Test email sending** before going live
4. **Monitor email logs** for delivery issues

## 💡 **Tips**

- **Development**: Use logging mode (no configuration needed)
- **Testing**: Use `test_email.py` to verify functionality
- **Production**: Configure real SMTP for actual email sending
- **Debugging**: Check server logs for email content and errors

Your email service is now robust and handles both development and production scenarios! 📧✨

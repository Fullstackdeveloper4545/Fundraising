# 📧 Email Testing Commands

## 🚀 Quick Test (No Authentication Required)

### 1. Check Email Configuration Status
```bash
curl -X GET "http://localhost:8000/api/v1/email-test/status-public"
```

### 2. Get Email Configuration Details
```bash
curl -X GET "http://localhost:8000/api/v1/email-test/config-public"
```

### 3. Send Simple Test Email
```bash
curl -X POST "http://localhost:8000/api/v1/email-test/test-simple-public" \
  -H "Content-Type: application/json" \
  -d '{"to_email": "your-email@example.com"}'
```

### 4. Send Advanced Test Email
```bash
curl -X POST "http://localhost:8000/api/v1/email-test/test-public" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@example.com",
    "subject": "Test Email from Fundraising Platform",
    "test_type": "simple"
  }'
```

## 🧪 Available Test Types

Replace `"test_type": "simple"` with any of these:

- `"simple"` - Basic test email
- `"welcome"` - Welcome email template
- `"password_reset"` - Password reset email template
- `"referral"` - Referral invitation email template
- `"donation"` - Donation confirmation email template
- `"campaign_update"` - Campaign update email template

## 📋 Example Commands

### Test Welcome Email
```bash
curl -X POST "http://localhost:8000/api/v1/email-test/test-public" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@example.com",
    "test_type": "welcome"
  }'
```

### Test Password Reset Email
```bash
curl -X POST "http://localhost:8000/api/v1/email-test/test-public" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@example.com",
    "test_type": "password_reset"
  }'
```

### Test Referral Email
```bash
curl -X POST "http://localhost:8000/api/v1/email-test/test-public" \
  -H "Content-Type: application/json" \
  -d '{
    "to_email": "your-email@example.com",
    "test_type": "referral"
  }'
```

## 🔧 Email Configuration

Make sure your `.env` file has these settings:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
FRONTEND_URL=https://srv1133545.hstgr.cloud
BACKEND_URL=https://srv1133545.hstgr.cloud
```

## 🎯 Quick Start

1. **Start your server:**
   ```bash
   cd Fundraising1/backend
   python start_dev.py
   ```

2. **Test email configuration (update host if running locally):**
   ```bash
   curl -X GET "https://srv1133545.hstgr.cloud/api/v1/email-test/status-public"
   ```

3. **Send a test email:**
   ```bash
   curl -X POST "https://srv1133545.hstgr.cloud/api/v1/email-test/test-simple-public" \
     -H "Content-Type: application/json" \
     -d '{"to_email": "your-email@example.com"}'
   ```

## 🐛 Troubleshooting

### If you get 403 Forbidden:
- Use the `-public` endpoints (no authentication required)
- Check that your server is running on port 8000

### If emails don't send:
- Check your `.env` file configuration
- Verify SMTP credentials
- Check spam folder
- Use Gmail App Password (not regular password)

### If you get connection errors:
- Make sure the server is running
- Check the URL is correct
- Verify the endpoint exists

## 📚 Interactive API Docs

Visit http://localhost:8000/docs to see all available endpoints and test them interactively.

---

**Happy Testing! 📧✨**

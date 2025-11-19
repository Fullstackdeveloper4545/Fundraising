# Fundraising Platform Backend

A comprehensive fundraising platform backend built with FastAPI, designed specifically for high school students to create campaigns and raise funds.

## Features

- **User Management**: Student registration, authentication, and profile management
- **Campaign Management**: Create, update, and manage fundraising campaigns
- **Payment Processing**: Integration with Stripe, PayPal, and Square
- **Referral System**: Students must refer 5 friends before creating campaigns
- **Student Highlights**: Weekly featured students and achievements
- **Company Partnerships**: Corporate sponsorships and grant programs
- **Receipt Generation**: Automated receipt generation for donations
- **Admin Dashboard**: Administrative access for platform management

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Supabase**: Backend-as-a-Service for database and authentication
- **PostgreSQL**: Database (via Supabase)
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation and settings management
- **Python 3.8+**: Programming language

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fundraising-platform/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Set up Supabase database**
   - Create a new Supabase project
   - Copy the database schema from `database/supabase_schema.sql`
   - Execute the SQL in your Supabase SQL Editor
   - Update your `.env` file with Supabase credentials

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# JWT Configuration
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Payment Gateway Configuration (Optional)
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
PAYPAL_CLIENT_ID=your_paypal_client_id
PAYPAL_CLIENT_SECRET=your_paypal_client_secret
SQUARE_APPLICATION_ID=your_square_application_id
SQUARE_ACCESS_TOKEN=your_square_access_token

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# App Configuration (Hostinger defaults)
FRONTEND_URL=https://srv1133545.hstgr.cloud
BACKEND_URL=https://srv1133545.hstgr.cloud
# Override these with http://localhost:* when running locally.
```

## Running the Application

### Quick Start (Recommended)

```bash
# Run the development startup script
python start_dev.py
```

### Manual Start

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Initial Setup

```bash
# Run the setup script to create .env file
python setup.py
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: https://srv1133545.hstgr.cloud/docs (use http://localhost:8000/docs for local dev)
- **ReDoc documentation**: https://srv1133545.hstgr.cloud/redoc
- **Health check**: https://srv1133545.hstgr.cloud/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

### Campaigns
- `POST /api/v1/campaigns/` - Create campaign
- `GET /api/v1/campaigns/` - Get all campaigns
- `GET /api/v1/campaigns/{id}` - Get specific campaign
- `PUT /api/v1/campaigns/{id}` - Update campaign
- `DELETE /api/v1/campaigns/{id}` - Delete campaign
- `POST /api/v1/campaigns/{id}/start` - Start campaign
- `GET /api/v1/campaigns/user/{user_id}` - Get user campaigns

### Payments
- `POST /api/v1/payments/` - Create payment/donation
- `GET /api/v1/payments/campaign/{campaign_id}` - Get campaign payments
- `GET /api/v1/payments/{payment_id}` - Get specific payment
- `POST /api/v1/payments/{payment_id}/process` - Process payment
- `POST /api/v1/payments/{payment_id}/refund` - Refund payment

### Referrals
- `POST /api/v1/referrals/` - Create referral
- `GET /api/v1/referrals/campaign/{campaign_id}` - Get campaign referrals
- `GET /api/v1/referrals/stats/{campaign_id}` - Get referral statistics
- `POST /api/v1/referrals/accept/{token}` - Accept referral

### Student Highlights
- `GET /api/v1/highlights/current` - Get current highlighted student
- `GET /api/v1/highlights/donors` - Get highlighted donors
- `GET /api/v1/highlights/weekly` - Get weekly highlights
- `GET /api/v1/highlights/student/{user_id}` - Get student achievements
- `POST /api/v1/highlights/create` - Create student highlight (admin)

### Admin
- `GET /api/v1/admin/stats` - Get platform statistics
- `GET /api/v1/admin/campaigns` - Get all campaigns
- `GET /api/v1/admin/users` - Get all users
- `POST /api/v1/admin/campaigns/{id}/feature` - Feature campaign

## Database Schema

The application uses the following main entities:

- **Users**: Student, admin, and company users
- **Campaigns**: Fundraising campaigns with goals and timelines
- **Payments**: Donation transactions
- **Referrals**: Invitation system for campaign requirements
- **Shoutouts**: Public messages from donors
- **Milestones**: Campaign progress markers
- **Receipts**: Automated receipt generation
- **Companies**: Corporate partners and sponsors
- **Student Highlights**: Weekly featured students

## Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Row Level Security (RLS) in Supabase
- Input validation with Pydantic
- CORS protection
- Rate limiting (recommended for production)

## Deployment

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

1. Set up Supabase project
2. Configure environment variables
3. Deploy to your preferred platform (Heroku, Railway, DigitalOcean, etc.)
4. Set up SSL certificates
5. Configure domain and DNS

## Testing

```bash
# Run tests (when implemented)
pytest tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For technical support or questions, please contact the development team or create an issue in the repository.

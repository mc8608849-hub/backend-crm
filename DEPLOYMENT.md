# Deployment Guide for Backend CRM

## Prerequisites

- Python 3.8+
- PostgreSQL (recommended for production)
- Docker (optional, for containerization)
- Git
- Your US phone number configured with a phone service provider

## Local Development

### 1. Setup Environment

```bash
# Clone the repository
git clone https://github.com/mc8608849-hub/backend-crm.git
cd backend-crm

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env`:

```env
# Database
DATABASE_URL=sqlite:///crm.db  # For development

# Authentication
SECRET_KEY=your-very-secret-key-change-this
AUTH_USERNAME=admin
AUTH_PASSWORD=your-secure-password

# ElevenLabs API
ELEVENLABS_API_KEY=your_api_key
ELEVENLABS_VOICE_ID=your_voice_id

# Phone Integration
CALLER_PHONE_NUMBER=+1234567890  # Your US phone number
PHONE_WEBHOOK_SECRET=your-webhook-secret
API_URL=http://localhost:8000
```

### 3. Run Locally

```bash
# Run the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at http://localhost:8000
# Interactive API docs at http://localhost:8000/docs
```

### 4. Test the API

```bash
# Install test dependencies
pip install pytest

# Run tests
pytest test_api.py -v

# Or run specific test class
pytest test_api.py::TestPeople -v
```

## Production Deployment

### Option 1: Heroku Deployment

#### Setup

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create your-crm-backend

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set AUTH_USERNAME=admin
heroku config:set AUTH_PASSWORD=secure-password
heroku config:set ELEVENLABS_API_KEY=your-api-key
heroku config:set ELEVENLABS_VOICE_ID=your-voice-id
heroku config:set CALLER_PHONE_NUMBER=+1234567890
heroku config:set PHONE_WEBHOOK_SECRET=your-webhook-secret
heroku config:set API_URL=https://your-crm-backend.herokuapp.com
```

#### Create Procfile

```txt
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Deploy

```bash
# Push to Heroku
git push heroku main

# View logs
heroku logs --tail
```

### Option 2: AWS Deployment (using Elastic Beanstalk)

#### Setup

```bash
# Install AWS CLI and EB CLI
pip install awsebcli

# Initialize EB app
eb init -p python-3.9 backend-crm --region us-east-1

# Create environment
eb create production

# Set environment variables
eb setenv \
  SECRET_KEY=your-secret-key \
  AUTH_USERNAME=admin \
  AUTH_PASSWORD=secure-password \
  ELEVENLABS_API_KEY=your-api-key \
  ELEVENLABS_VOICE_ID=your-voice-id \
  CALLER_PHONE_NUMBER=+1234567890 \
  PHONE_WEBHOOK_SECRET=your-webhook-secret \
  DATABASE_URL=postgresql://user:password@db-host:5432/crm_db

# Deploy
eb deploy
```

### Option 3: Docker Deployment

#### Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: crm_db
      POSTGRES_USER: crm_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://crm_user:secure_password@db:5432/crm_db
      SECRET_KEY: your-secret-key
      AUTH_USERNAME: admin
      AUTH_PASSWORD: secure-password
      ELEVENLABS_API_KEY: your-api-key
      ELEVENLABS_VOICE_ID: your-voice-id
      CALLER_PHONE_NUMBER: +1234567890
      PHONE_WEBHOOK_SECRET: your-webhook-secret
    depends_on:
      - db

volumes:
  postgres_data:
```

#### Deploy with Docker

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

### Option 4: DigitalOcean App Platform

#### Create app.yaml

```yaml
name: backend-crm
services:
  - name: api
    github:
      repo: mc8608849-hub/backend-crm
      branch: main
    build_command: pip install -r requirements.txt
    run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
    envs:
      - key: DATABASE_URL
        scope: RUN_AND_BUILD_TIME
        value: ${db.connection_string}
      - key: SECRET_KEY
        scope: RUN_AND_BUILD_TIME
        value: ${SECRET_KEY}
      - key: ELEVENLABS_API_KEY
        scope: RUN_AND_BUILD_TIME
        value: ${ELEVENLABS_API_KEY}
    http_port: 8080
  - name: db
    engine: PG
    version: "13"
```

## Configuration for Production

### Security Best Practices

1. **Environment Variables**: Never commit `.env` file
   ```bash
   echo ".env" >> .gitignore
   ```

2. **Database**: Use PostgreSQL in production
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/crm_db
   ```

3. **HTTPS**: Enable SSL/TLS at your hosting provider

4. **CORS**: Update allowed origins
   ```python
   allow_origins=["https://yourdomain.com"]
   ```

5. **API Keys**: Use strong, random SECRET_KEY
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

### Database Migrations

```bash
# Install Alembic
pip install alembic

# Initialize migrations
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### Monitoring & Logging

1. **Application Logging**
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```

2. **Uptime Monitoring**: Use services like:
   - UptimeRobot
   - Pingdom
   - New Relic

3. **Error Tracking**: Use Sentry
   ```bash
   pip install sentry-sdk
   ```

## Phone Integration Setup

### Setting Up Your Webhook

1. **Configure your phone service provider** to send webhooks to:
   ```
   https://your-domain.com/api/phone/incoming-webhook
   ```

2. **Add webhook secret** to `.env`:
   ```env
   PHONE_WEBHOOK_SECRET=your-random-secret
   ```

3. **Test webhook**:
   ```bash
   curl -X POST "https://your-domain.com/api/phone/incoming-webhook" \
     -H "Content-Type: application/json" \
     -H "X-Webhook-Secret: your-random-secret" \
     -d '{
       "phone_number": "+1234567890",
       "from_number": "+9876543210",
       "call_id": "test_call_001",
       "timestamp": "2026-05-29T15:30:00Z"
     }'
   ```

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL backup
pg_dump crm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql crm_db < backup_20260529_150000.sql
```

## Troubleshooting

### Issue: Database Connection Error
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

### Issue: 401 Unauthorized
- Check SECRET_KEY is set correctly
- Verify JWT token is valid
- Check Authorization header format

### Issue: Phone webhooks not received
- Verify webhook URL is publicly accessible
- Check firewall rules
- Test with curl command above
- Check logs for errors

## Performance Optimization

### Enable Caching

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
from redis import asyncio as aioredis

redis = await aioredis.from_url("redis://localhost")
FastAPICache2.init(RedisBackend(redis), prefix="crm-cache")
```

### Database Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
)
```

## Support

For issues or questions:
- Check GitHub Issues
- Review logs
- Test endpoints with `/docs` interface
- Contact your hosting provider support

---

**Happy deploying! 🚀**

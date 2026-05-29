# Backend CRM

A FastAPI-based CRM backend for debt collection and sales management with AI voice integration.

## Features

- **Contact Management**: CRUD operations for people/debtors
- **Call Logging**: Track calls with transcripts and status
- **Email Logging**: Log inbound/outbound emails with AI summaries
- **AI Voice**: ElevenLabs text-to-speech integration
- **JWT Authentication**: Secure API endpoints
- **SQLModel**: Type-safe database models

## Tech Stack

- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite/PostgreSQL
- ElevenLabs API
- JWT Authentication

## Setup

### 1. Clone and Install

```bash
git clone https://github.com/mc8608849-hub/backend-crm.git
cd backend-crm
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run the Server

```bash
uvicorn app.main:app --reload
```

Server runs at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info

### People/Debtors
- `POST /api/people/` - Create new person
- `GET /api/people/` - List all people
- `GET /api/people/{person_id}` - Get person details
- `PUT /api/people/{person_id}` - Update person
- `DELETE /api/people/{person_id}` - Delete person

### Call Logs
- `POST /api/calls/` - Create call log
- `GET /api/calls/` - List all calls
- `GET /api/calls/person/{person_id}` - Get person's calls
- `GET /api/calls/{call_id}` - Get call details
- `PUT /api/calls/{call_id}` - Update call with results

### Voice
- `POST /api/voice/clone` - Generate speech from text

## Project Structure

```
backend-crm/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app setup
│   ├── database.py       # DB configuration
│   ├── models.py         # SQLModel schemas
│   ├── schemas.py        # Pydantic read models
│   ├── auth.py           # JWT authentication
│   ├── person_router.py  # People CRUD
│   ├── ai_calls.py       # Call logging
│   └── ai_voice.py       # Voice API
├── .env.example
├── requirements.txt
└── README.md
```

## Usage Example

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"changeme"}'

# Response:
# {"access_token":"eyJ0eXAiOiJKV1QiLCJhbGc...","token_type":"bearer"}

# 2. Create person (use the token from login)
curl -X POST "http://localhost:8000/api/people/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"John Doe",
    "phone":"555-1234",
    "email":"john@example.com",
    "amount_owed":5000,
    "sale_date":"2026-01-15T00:00:00",
    "state":"CA",
    "county":"Los Angeles"
  }'

# 3. List all people
curl -X GET "http://localhost:8000/api/people/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Database Models

### Person
```python
- id: int (primary key)
- name: str
- phone: str
- email: str
- amount_owed: float
- sale_date: datetime
- state: str
- county: str
```

### CallLog
```python
- id: int (primary key)
- person_id: int (foreign key)
- started_at: datetime
- call_sid: str (optional)
- result: str (optional)
- transcript: str (optional)
- status: str
```

### EmailLog
```python
- id: int (primary key)
- person_id: int (foreign key)
- direction: str ('inbound'/'outbound')
- subject: str
- body: str
- timestamp: datetime
- ai_summary: str (optional)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|----------|
| `DATABASE_URL` | Database connection string | `sqlite:///crm.db` |
| `SECRET_KEY` | JWT signing key | Required for production |
| `AUTH_USERNAME` | Admin username | `admin` |
| `AUTH_PASSWORD` | Admin password | `password` |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Required for voice |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID | Required for voice |

## Next Steps

- [ ] Add email logging endpoints
- [ ] Integrate Twilio for voice calls
- [ ] Add AI call summaries
- [ ] Build React frontend with react-simple-maps
- [ ] Add database migrations (Alembic)
- [ ] Add input validation
- [ ] Deploy to production
- [ ] Add WebSocket support for real-time updates

## License

MIT
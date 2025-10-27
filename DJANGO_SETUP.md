# SafyCore Backend - Django + Supabase Setup Guide

## Overview

SafyCore Backend has been upgraded to use **Django REST Framework** with **Supabase** for user authentication and data storage. Each user has their own isolated data with Row Level Security (RLS).

## Features

- **User Authentication**: Signup, login, logout using Supabase Auth
- **User Isolation**: Each user's chat history is completely isolated using Supabase RLS
- **Session Management**: Multiple conversation sessions per user
- **AI Chat**: Groq-powered chatbot with streaming support
- **Training Data**: Custom training data per user and session
- **RESTful API**: Clean API design with Django REST Framework

## Architecture

```
┌─────────────────┐
│   Frontend      │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  Django API     │
│  (Backend)      │
└────┬────────┬───┘
     │        │
     │        └──────────────┐
     │                       │
     ▼                       ▼
┌─────────────┐      ┌──────────────┐
│  Supabase   │      │   Groq AI    │
│  (Auth+DB)  │      │   (Chat)     │
└─────────────┘      └──────────────┘
```

## Prerequisites

1. **Python 3.12+** installed
2. **Supabase Account** - [Sign up here](https://supabase.com)
3. **Groq API Key** - [Get key here](https://console.groq.com/keys)

## Step 1: Supabase Setup

### 1.1 Create a Supabase Project

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Click "New Project"
3. Fill in project details and create

### 1.2 Run SQL Setup

1. In your Supabase dashboard, go to **SQL Editor**
2. Open the file `supabase_setup.sql` from this project
3. Copy and paste the entire SQL script into the editor
4. Click "Run" to execute

This will create:
- `messages` table with RLS enabled
- `training_data` table with RLS enabled
- Indexes for performance
- Policies to ensure user data isolation

### 1.3 Get API Keys

1. In Supabase dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL** (e.g., `https://xxxxx.supabase.co`)
   - **anon public** key (for client-side)
   - **service_role** key (for server-side admin operations)

## Step 2: Django Project Setup

### 2.1 Install Dependencies

```bash
# Install all required packages
py -m pip install -r requirements.txt
```

### 2.2 Configure Environment Variables

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```env
   # Django Configuration
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=*

   # Supabase Configuration
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key-here
   SUPABASE_SERVICE_KEY=your-service-role-key-here

   # Groq AI Configuration
   GROQ_API_KEY=your-groq-api-key-here
   ```

### 2.3 Run Migrations

```bash
# Apply Django database migrations
py manage.py migrate

# Create admin superuser (optional)
py manage.py createsuperuser
```

### 2.4 Start the Server

```bash
# Run development server
py manage.py runserver

# Server will start at: http://127.0.0.1:8000
```

## API Endpoints

### Authentication Endpoints

#### 1. Signup
```http
POST /api/auth/signup/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  },
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-token-here"
}
```

#### 2. Login
```http
POST /api/auth/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  },
  "access_token": "jwt-token-here",
  "refresh_token": "refresh-token-here"
}
```

#### 3. Get Profile (Authenticated)
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "created_at": "2025-01-01T00:00:00Z",
    "default_session_id": "session-123"
  }
}
```

#### 4. Logout (Authenticated)
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

### Chat Endpoints

#### 1. Send Chat Message (Non-streaming)
```http
POST /api/chat/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Tell me about the Honda Civic",
  "session_id": "session-123",
  "training_data": "Honda Civic 2022, silver, 1.5L turbo, 18,000 km, $25,000"
}
```

**Response:**
```json
{
  "response": "The Honda Civic is a 2022 model in silver with a 1.5L turbo engine.",
  "session_id": "session-123"
}
```

#### 2. Send Chat Message (Streaming)
```http
POST /api/chat/stream/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "message": "Tell me about the Honda Civic",
  "session_id": "session-123"
}
```

**Response:** Text stream (one token at a time)

#### 3. Get Conversation History
```http
GET /api/chat/conversation/<session_id>/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "session_id": "session-123",
  "messages": [
    {
      "id": "uuid-1",
      "role": "system",
      "content": "You are a helpful assistant...",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "uuid-2",
      "role": "user",
      "content": "Tell me about the Honda Civic",
      "created_at": "2025-01-01T00:00:01Z"
    },
    {
      "id": "uuid-3",
      "role": "assistant",
      "content": "The Honda Civic is a 2022 model...",
      "created_at": "2025-01-01T00:00:02Z"
    }
  ]
}
```

#### 4. Clear Conversation
```http
DELETE /api/chat/conversation/<session_id>/clear/
Authorization: Bearer <access_token>
```

#### 5. Get All User Sessions
```http
GET /api/chat/sessions/
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session-123",
      "title": "Tell me about the Honda Civic",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:05:00Z"
    }
  ]
}
```

## Data Isolation

### How RLS Works

Row Level Security (RLS) in Supabase ensures that:

1. **User A** can ONLY see their own messages
2. **User B** can ONLY see their own messages
3. Even with the same `session_id`, users cannot access each other's data

### Policies Applied

```sql
-- Messages table policy
CREATE POLICY "Users can only access their own messages"
  ON messages
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- Training data table policy
CREATE POLICY "Users can only access their own training data"
  ON training_data
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

## Frontend Integration Example

```javascript
// 1. Signup
const signup = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/auth/signup/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
  return data;
};

// 2. Send chat message
const sendMessage = async (message, sessionId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/chat/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId
    })
  });
  return await response.json();
};

// 3. Stream chat response
const streamMessage = async (message, sessionId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/chat/stream/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      message: message,
      session_id: sessionId
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    console.log(chunk); // Display token
  }
};
```

## Testing the API

### Using cURL

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 2. Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'

# 3. Send chat (replace YOUR_TOKEN)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "Hello", "session_id": "test-session"}'
```

### Using Postman

1. Create a new request
2. Set method to `POST`
3. URL: `http://localhost:8000/api/auth/signup/`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
   ```json
   {
     "email": "test@example.com",
     "password": "password123"
   }
   ```
6. Send request
7. Copy the `access_token` from response
8. Use it in `Authorization: Bearer <token>` header for other requests

## Project Structure

```
SafyCore-backend/
├── safycore_backend/          # Django project settings
│   ├── settings.py            # Configuration
│   ├── urls.py                # Main URL routing
│   └── supabase_client.py     # Supabase client utilities
├── users/                     # User authentication app
│   ├── models.py              # UserProfile model
│   ├── views.py               # Auth endpoints
│   ├── authentication.py      # JWT auth backend
│   └── urls.py                # Auth URL routing
├── chat/                      # Chat functionality app
│   ├── models.py              # ConversationSession model
│   ├── views.py               # Chat endpoints
│   └── urls.py                # Chat URL routing
├── manage.py                  # Django management script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── supabase_setup.sql         # Supabase database setup
└── DJANGO_SETUP.md           # This file
```

## Troubleshooting

### 1. "SUPABASE_URL must be set"
- Make sure you've copied `.env.example` to `.env`
- Add your Supabase credentials to `.env`

### 2. "Invalid token" errors
- Check that you're using the correct access token
- Tokens expire - login again to get a new one

### 3. "Table does not exist" errors
- Run the `supabase_setup.sql` script in Supabase SQL Editor
- Check that tables were created successfully

### 4. Can see other users' data
- Verify RLS is enabled: `ALTER TABLE messages ENABLE ROW LEVEL SECURITY;`
- Check policies are created in Supabase dashboard

### 5. "Module not found" errors
- Run: `py -m pip install -r requirements.txt`

## Production Deployment

### Environment Variables for Production

```env
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
DJANGO_SECRET_KEY=<generate-strong-secret-key>
```

### Security Checklist

- [ ] Set `DEBUG=False`
- [ ] Use strong `DJANGO_SECRET_KEY`
- [ ] Restrict `ALLOWED_HOSTS`
- [ ] Restrict `CORS_ALLOW_ALL_ORIGINS` to specific domains
- [ ] Use HTTPS
- [ ] Keep `SUPABASE_SERVICE_KEY` secret (never expose to frontend)
- [ ] Enable Supabase email verification
- [ ] Set up rate limiting
- [ ] Enable Django's security middleware

## Next Steps

1. ✅ Set up Supabase tables with RLS
2. ✅ Configure environment variables
3. ✅ Run Django migrations
4. ✅ Test authentication endpoints
5. ✅ Test chat endpoints
6. 🔲 Build frontend UI
7. 🔲 Deploy to production

## Support

For issues or questions:
- Check Supabase documentation: https://supabase.com/docs
- Check Django documentation: https://docs.djangoproject.com
- Review the code comments in the project

Happy coding! 🚀

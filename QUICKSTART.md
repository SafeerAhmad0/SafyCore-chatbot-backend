# SafyCore Backend - Quick Start Guide

## 🚀 Get Up and Running in 5 Minutes

### Step 1: Supabase Setup (2 minutes)

1. **Create Supabase Project**
   - Go to https://supabase.com/dashboard
   - Click "New Project"
   - Create your project

2. **Run SQL Setup**
   - Open Supabase SQL Editor
   - Copy contents of `supabase_setup.sql`
   - Paste and run

3. **Get API Keys**
   - Go to Settings → API
   - Copy:
     - Project URL
     - `anon` key
     - `service_role` key

### Step 2: Configure Django (1 minute)

1. **Update `.env` file**
   ```env
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key
   SUPABASE_SERVICE_KEY=your-service-role-key
   GROQ_API_KEY=your-existing-groq-key
   ```

### Step 3: Start Server (1 minute)

```bash
# Migrations already done!
py manage.py runserver
```

Server starts at: http://127.0.0.1:8000

### Step 4: Test API (1 minute)

#### Test in Browser
Visit: http://127.0.0.1:8000/api/

You should see:
```json
{
  "message": "SafyCore Backend API",
  "version": "2.0",
  "endpoints": { ... }
}
```

#### Test Signup (cURL)
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"test123\"}"
```

## 📝 What Changed from FastAPI?

| Feature | Old (FastAPI) | New (Django) |
|---------|---------------|--------------|
| **Storage** | In-memory dict | Supabase with RLS |
| **Users** | None | Full auth system |
| **Data Isolation** | None | Per-user with RLS |
| **Framework** | FastAPI | Django REST |
| **Database** | None | SQLite (Django) + Supabase |

## 🔑 Key Differences

### Authentication Required
All chat endpoints now require authentication:
```http
Authorization: Bearer <access_token>
```

### User-Specific Data
- Each user sees only their own conversations
- Session IDs are unique per user
- Training data is isolated per user

### New Endpoints

**Authentication:**
- `POST /api/auth/signup/` - Create account
- `POST /api/auth/login/` - Get access token
- `GET /api/auth/profile/` - Get user info
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset/confirm/` - Confirm reset
- `POST /api/auth/change-password/` - Change password

**Chat:**
- `POST /api/chat/` - Send message (non-streaming)
- `POST /api/chat/stream/` - Send message (streaming)
- `GET /api/chat/sessions/` - Get all sessions
- `GET /api/chat/conversation/<id>/` - Get history
- `DELETE /api/chat/conversation/<id>/clear/` - Clear history

## 📋 Complete Example Flow

### 1. Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "user": {"id": "...", "email": "user@test.com"}
}
```

### 2. Send Chat Message
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGc..." \
  -d '{"message":"Hello","session_id":"test-1"}'
```

**Response:**
```json
{
  "response": "Hello! How can I help you today?",
  "session_id": "test-1"
}
```

### 3. Get Conversation History
```bash
curl http://localhost:8000/api/chat/conversation/test-1/ \
  -H "Authorization: Bearer eyJhbGc..."
```

## 🔒 Security Features

✅ **JWT Authentication** via Supabase
✅ **Row Level Security** - Users can't access other users' data
✅ **Password Hashing** - Handled by Supabase Auth
✅ **CORS Protection** - Configurable origins
✅ **Token Expiration** - Automatic session timeout

## 🐛 Troubleshooting

### "SUPABASE_URL must be set"
→ Update your `.env` file with Supabase credentials

### "Invalid token"
→ Get a new token by logging in again

### "Module not found"
→ Run: `py -m pip install -r requirements.txt`

### "Table does not exist"
→ Run `supabase_setup.sql` in Supabase SQL Editor

## 📚 Full Documentation

See `DJANGO_SETUP.md` for complete documentation including:
- Detailed architecture
- All API endpoints
- Frontend integration examples
- Production deployment guide

## 🎯 Next Steps

1. ✅ Test signup and login
2. ✅ Test chat endpoints
3. 🔲 Build your frontend
4. 🔲 Customize for your use case
5. 🔲 Deploy to production

Need help? Check `DJANGO_SETUP.md` for detailed guides!

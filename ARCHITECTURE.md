# SafyCore Backend - Architecture Overview

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                  │
│  (React, Vue, or any JS framework)                               │
│                                                                   │
│  - Login/Signup UI                                                │
│  - Chat Interface                                                 │
│  - Session Management                                             │
└────────────────┬─────────────────────────────────────────────────┘
                 │
                 │ HTTP REST API
                 │ Authorization: Bearer <JWT>
                 │
┌────────────────▼─────────────────────────────────────────────────┐
│                    DJANGO REST FRAMEWORK                          │
│                    (SafyCore Backend)                             │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  API Layer (safycore_backend/urls.py)                       │ │
│  │  /api/auth/*  →  /api/chat/*                                │ │
│  └────────────┬──────────────────────┬──────────────────────────┘ │
│               │                      │                            │
│  ┌────────────▼──────────┐  ┌───────▼──────────────┐            │
│  │   Users App            │  │   Chat App            │            │
│  │                        │  │                       │            │
│  │ - SignupView           │  │ - ChatView            │            │
│  │ - LoginView            │  │ - ChatStreamView      │            │
│  │ - ProfileView          │  │ - ConversationHistory │            │
│  │ - LogoutView           │  │ - ClearConversation   │            │
│  │                        │  │ - UserSessionsView    │            │
│  │ - SupabaseAuth         │  │                       │            │
│  │   (JWT validation)     │  │ - strip_markdown()    │            │
│  └────────────┬───────────┘  └───────┬───────────────┘            │
│               │                      │                            │
│  ┌────────────▼──────────────────────▼──────────────────────────┐ │
│  │  Supabase Client (safycore_backend/supabase_client.py)      │ │
│  │  - get_supabase_client()                                     │ │
│  │  - get_user_supabase_client(token)  ← RLS Enforced          │ │
│  │  - get_supabase_admin_client()                               │ │
│  └────────────┬───────────────────────────────┬─────────────────┘ │
│               │                               │                   │
└───────────────┼───────────────────────────────┼───────────────────┘
                │                               │
                │                               │
     ┌──────────▼──────────┐         ┌─────────▼──────────┐
     │    SUPABASE         │         │    GROQ AI         │
     │                     │         │                    │
     │ ┌─────────────────┐ │         │  - LLM Models      │
     │ │  Auth Service   │ │         │  - Chat Streaming  │
     │ │  - JWT Tokens   │ │         │  - Completions     │
     │ │  - User Mgmt    │ │         │                    │
     │ └─────────────────┘ │         └────────────────────┘
     │                     │
     │ ┌─────────────────┐ │
     │ │  PostgreSQL DB  │ │
     │ │                 │ │
     │ │ ┌─────────────┐ │ │
     │ │ │  messages   │ │ │ ← RLS Enabled
     │ │ │  user_id    │ │ │
     │ │ │  session_id │ │ │
     │ │ │  role       │ │ │
     │ │ │  content    │ │ │
     │ │ └─────────────┘ │ │
     │ │                 │ │
     │ │ ┌─────────────┐ │ │
     │ │ │training_data│ │ │ ← RLS Enabled
     │ │ │  user_id    │ │ │
     │ │ │  session_id │ │ │
     │ │ │  content    │ │ │
     │ │ └─────────────┘ │ │
     │ └─────────────────┘ │
     └─────────────────────┘
```

## Data Flow

### 1. User Signup Flow

```
┌─────────┐                          ┌─────────┐                     ┌──────────┐
│ User    │                          │ Django  │                     │ Supabase │
└────┬────┘                          └────┬────┘                     └────┬─────┘
     │                                    │                               │
     │  POST /api/auth/signup/            │                               │
     │  {email, password}                 │                               │
     ├───────────────────────────────────►│                               │
     │                                    │                               │
     │                                    │  supabase.auth.sign_up()      │
     │                                    ├──────────────────────────────►│
     │                                    │                               │
     │                                    │  ◄────────────────────────────┤
     │                                    │  {user, session, tokens}      │
     │                                    │                               │
     │                                    │  Create UserProfile           │
     │                                    │  in Django DB                 │
     │                                    │                               │
     │  ◄─────────────────────────────────┤                               │
     │  {user, access_token, ...}         │                               │
     │                                    │                               │
```

### 2. User Login Flow

```
┌─────────┐                          ┌─────────┐                     ┌──────────┐
│ User    │                          │ Django  │                     │ Supabase │
└────┬────┘                          └────┬────┘                     └────┬─────┘
     │                                    │                               │
     │  POST /api/auth/login/             │                               │
     │  {email, password}                 │                               │
     ├───────────────────────────────────►│                               │
     │                                    │                               │
     │                                    │  supabase.auth.sign_in()      │
     │                                    ├──────────────────────────────►│
     │                                    │                               │
     │                                    │  ◄────────────────────────────┤
     │                                    │  {user, session, tokens}      │
     │                                    │                               │
     │  ◄─────────────────────────────────┤                               │
     │  {user, access_token, ...}         │                               │
     │                                    │                               │
     │  Store token in localStorage       │                               │
     │                                    │                               │
```

### 3. Chat Message Flow

```
┌─────────┐                ┌─────────┐              ┌──────────┐         ┌────────┐
│ User    │                │ Django  │              │ Supabase │         │ Groq   │
└────┬────┘                └────┬────┘              └────┬─────┘         └───┬────┘
     │                          │                        │                   │
     │  POST /api/chat/         │                        │                   │
     │  Authorization: Bearer   │                        │                   │
     │  {message, session_id}   │                        │                   │
     ├─────────────────────────►│                        │                   │
     │                          │                        │                   │
     │                          │  Validate JWT Token    │                   │
     │                          │  Extract user_id       │                   │
     │                          │                        │                   │
     │                          │  SELECT messages       │                   │
     │                          │  WHERE user_id=X       │                   │
     │                          │  AND session_id=Y      │                   │
     │                          ├───────────────────────►│                   │
     │                          │                        │                   │
     │                          │  ◄─────────────────────┤                   │
     │                          │  [user's messages]     │                   │
     │                          │  (RLS filtered)        │                   │
     │                          │                        │                   │
     │                          │  INSERT user message   │                   │
     │                          ├───────────────────────►│                   │
     │                          │                        │                   │
     │                          │  Call Groq API         │                   │
     │                          │  with conversation     │                   │
     │                          ├───────────────────────────────────────────►│
     │                          │                        │                   │
     │                          │  ◄─────────────────────────────────────────┤
     │                          │  AI response           │                   │
     │                          │                        │                   │
     │                          │  INSERT assistant msg  │                   │
     │                          ├───────────────────────►│                   │
     │                          │                        │                   │
     │  ◄───────────────────────┤                        │                   │
     │  {response, session_id}  │                        │                   │
     │                          │                        │                   │
```

### 4. Row Level Security (RLS) in Action

```
User A (user_id: aaa-111)                User B (user_id: bbb-222)
         │                                        │
         │                                        │
         ▼                                        ▼
┌────────────────────┐                  ┌────────────────────┐
│ Request messages   │                  │ Request messages   │
│ for session "chat" │                  │ for session "chat" │
└──────┬─────────────┘                  └──────┬─────────────┘
       │                                        │
       │                                        │
       ▼                                        ▼
┌──────────────────────────────────────────────────────────────┐
│                     SUPABASE (RLS)                            │
│                                                               │
│  Query: SELECT * FROM messages WHERE session_id = 'chat'     │
│                                                               │
│  RLS Policy Applied:                                          │
│  ├─ User A sees: WHERE user_id = 'aaa-111'                   │
│  └─ User B sees: WHERE user_id = 'bbb-222'                   │
│                                                               │
└──────┬────────────────────────────────────────┬──────────────┘
       │                                        │
       ▼                                        ▼
┌────────────────────┐                  ┌────────────────────┐
│ Returns only       │                  │ Returns only       │
│ User A's messages  │                  │ User B's messages  │
│ from "chat"        │                  │ from "chat"        │
└────────────────────┘                  └────────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: HTTPS/TLS                                               │
│ - Encrypts data in transit                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ Layer 2: CORS                                                    │
│ - Controls which origins can access API                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ Layer 3: JWT Authentication                                      │
│ - Validates user identity via Supabase tokens                    │
│ - Django middleware: SupabaseAuthentication                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ Layer 4: DRF Permissions                                         │
│ - IsAuthenticated: Ensures user is logged in                     │
│ - AllowAny: Only for signup/login                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│ Layer 5: Row Level Security (RLS)                                │
│ - Database-level isolation                                       │
│ - Users can ONLY access their own rows                           │
│ - Policy: auth.uid() = user_id                                   │
└──────────────────────────────────────────────────────────────────┘
```

## Database Schema

### Django Database (SQLite)

```sql
-- User Profiles
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE,      -- Supabase user UUID
    email VARCHAR(254) UNIQUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    default_session_id VARCHAR(255)
);

-- Conversation Sessions
CREATE TABLE conversation_sessions (
    id INTEGER PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE,
    user_id INTEGER REFERENCES user_profiles(id),
    title VARCHAR(255),
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Supabase Database (PostgreSQL)

```sql
-- Messages (Chat History)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    session_id VARCHAR(255) NOT NULL,
    role VARCHAR(50) CHECK (role IN ('system', 'user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_messages_user_session ON messages(user_id, session_id);

-- RLS Policy
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own messages"
    ON messages FOR ALL
    USING (auth.uid() = user_id);

-- Training Data
CREATE TABLE training_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    session_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_training_data_user_session ON training_data(user_id, session_id);

-- RLS Policy
ALTER TABLE training_data ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their own training data"
    ON training_data FOR ALL
    USING (auth.uid() = user_id);
```

## Authentication Flow Diagram

```
┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ 1. POST /api/auth/signup/
       │    {email, password}
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Django: SignupView                                       │
│                                                           │
│  1. Receive request                                       │
│  2. Call: supabase.auth.sign_up()                        │
│  3. Create UserProfile in Django DB                       │
│  4. Return: {user, access_token, refresh_token}          │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Supabase    │
│  Auth        │
│              │
│  - Hashes    │
│    password  │
│  - Creates   │
│    user      │
│  - Issues    │
│    JWT       │
└──────────────┘

--- Subsequent Requests ---

┌──────────────┐
│   Browser    │
└──────┬───────┘
       │
       │ 2. POST /api/chat/
       │    Authorization: Bearer <JWT>
       │    {message, session_id}
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Django: SupabaseAuthentication Middleware               │
│                                                          │
│  1. Extract JWT from header                              │
│  2. Call: supabase.auth.get_user(jwt)                    │
│  3. Validate token                                       │
│  4. Get/Create UserProfile                               │
│  5. Attach to request: request.user                      │
│  6. Attach token: request.supabase_token                 │
└──────┬───────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────────────────┐
│  Django: ChatView                                         │
│                                                           │
│  1. Access: request.user (authenticated)                  │
│  2. Query Supabase with user's token                      │
│  3. RLS automatically filters by user_id                  │
│  4. Process & return response                             │
└──────────────────────────────────────────────────────────┘
```

## Component Breakdown

### Django Apps

#### 1. **safycore_backend** (Main Project)
- `settings.py` - Configuration
- `urls.py` - URL routing
- `supabase_client.py` - Supabase utilities

#### 2. **users** (Authentication App)
- `models.py` - UserProfile model
- `views.py` - Signup, Login, Logout, Profile
- `authentication.py` - SupabaseAuthentication class
- `urls.py` - `/api/auth/*` routes

#### 3. **chat** (Chat App)
- `models.py` - ConversationSession model
- `views.py` - Chat, Stream, History, Clear
- `urls.py` - `/api/chat/*` routes

## Technology Stack

```
┌─────────────────────────────────────────────────┐
│               Backend Stack                     │
├─────────────────────────────────────────────────┤
│ Framework        │ Django 5.2.7                 │
│ API              │ Django REST Framework 3.16   │
│ Database (Local) │ SQLite 3                     │
│ Database (Cloud) │ Supabase PostgreSQL          │
│ Authentication   │ Supabase Auth (JWT)          │
│ AI               │ Groq API                     │
│ CORS             │ django-cors-headers          │
│ Environment      │ python-dotenv                │
└─────────────────────────────────────────────────┘
```

## Performance Considerations

### 1. Database Indexes

```sql
-- Speeds up user-session queries
CREATE INDEX idx_messages_user_session ON messages(user_id, session_id);
CREATE INDEX idx_training_data_user_session ON training_data(user_id, session_id);

-- Speeds up time-based queries
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
```

### 2. Connection Pooling
- Supabase handles connection pooling automatically
- Django uses connection pooling for local DB

### 3. Caching Opportunities
- User profiles (Django cache)
- Training data (Redis/Memcached)
- JWT validation results (short-lived cache)

### 4. Streaming Responses
- Reduces perceived latency
- Better UX for long responses
- Implemented via `StreamingHttpResponse`

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Production Setup                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Frontend (Vercel/Netlify)                                  │
│       ↓                                                     │
│  Nginx/Load Balancer                                        │
│       ↓                                                     │
│  Django (Gunicorn) ──────┬────→ Supabase (Auth + DB)        │
│                          │                                  │
│                          └────→ Groq AI                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Scaling Strategy

### Horizontal Scaling

```
                 ┌─────────────────┐
                 │  Load Balancer  │
                 └────────┬────────┘
                          │
         ┌────────────────┼───────────────┐
         │                │               │
    ┌────▼────┐      ┌────▼────┐     ┌────▼────┐
    │Django 1 │      │Django 2 │     │Django 3 │
    └────┬────┘      └────┬────┘     └────┬────┘
         │                │               │
         └────────────────┼───────────────┘
                          │
                   ┌──────▼──────┐
                   │  Supabase   │
                   │  (Managed)  │
                   └─────────────┘
```

---

This architecture provides:
✅ **Security**: Multiple layers of protection
✅ **Scalability**: Can handle growing users
✅ **Maintainability**: Clean separation of concerns
✅ **Performance**: Optimized queries with indexes
✅ **Isolation**: Complete user data separation
# SafyCore API Endpoints - Quick Reference

## Base URL

```
http://localhost:8000/api
```

---

## Authentication Endpoints

### 1. Signup

**POST** `/auth/signup/`

Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (201):**
```json
{
  "message": "User created successfully",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "eyJhbGciOiJIUzI1..."
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

---

### 2. Login

**POST** `/auth/login/`

Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com"
  },
  "access_token": "eyJhbGciOiJIUzI1...",
  "refresh_token": "eyJhbGciOiJIUzI1..."
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'
```

---

### 3. Logout

**POST** `/auth/logout/`

Logout current user. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Logout successful"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 4. Get Profile

**GET** `/auth/profile/`

Get current user profile. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
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

**cURL:**
```bash
curl http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 5. Update Profile

**PATCH** `/auth/profile/`

Update user profile. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "default_session_id": "new-session-id"
}
```

**Response (200):**
```json
{
  "message": "Profile updated successfully",
  "user": {
    "id": "uuid-here",
    "email": "user@example.com",
    "default_session_id": "new-session-id"
  }
}
```

**cURL:**
```bash
curl -X PATCH http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"default_session_id":"new-session"}'
```

---

### 6. Request Password Reset

**POST** `/auth/password-reset/`

Send password reset email.

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response (200):**
```json
{
  "message": "Password reset email sent. Please check your inbox.",
  "email": "user@example.com"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com"}'
```

---

### 7. Confirm Password Reset

**POST** `/auth/password-reset/confirm/`

Reset password with token from email.

**Request:**
```json
{
  "access_token": "token-from-email",
  "new_password": "newSecurePass123"
}
```

**Response (200):**
```json
{
  "message": "Password updated successfully. You can now login with your new password."
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "access_token":"TOKEN_FROM_EMAIL",
    "new_password":"newPass123"
  }'
```

---

### 8. Change Password

**POST** `/auth/change-password/`

Change password for logged-in user. **Requires authentication.**

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "current_password": "oldPassword123",
  "new_password": "newSecurePass456"
}
```

**Response (200):**
```json
{
  "message": "Password changed successfully"
}
```

**Error (400):**
```json
{
  "error": "Current password is incorrect"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password":"oldPass",
    "new_password":"newPass123"
  }'
```

---

## Chat Endpoints

All chat endpoints **require authentication**.

### 9. Send Chat Message

**POST** `/chat/`

Send a chat message (non-streaming).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "chat-session-1",
  "training_data": "Optional training data for first message"
}
```

**Response (200):**
```json
{
  "response": "I'm doing well, thank you for asking!",
  "session_id": "chat-session-1"
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message":"Hello!",
    "session_id":"test-session"
  }'
```

---

### 10. Send Chat Message (Streaming)

**POST** `/chat/stream/`

Send a chat message with streaming response.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request:**
```json
{
  "message": "Tell me a story",
  "session_id": "chat-session-1",
  "training_data": "Optional training data"
}
```

**Response:** Text stream (tokens arrive one by one)

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/api/chat/stream/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'Hello',
    session_id: 'session-1'
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
```

---

### 11. Get Conversation History

**GET** `/chat/conversation/<session_id>/`

Get all messages for a conversation session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "session_id": "chat-session-1",
  "messages": [
    {
      "id": "uuid-1",
      "user_id": "user-uuid",
      "session_id": "chat-session-1",
      "role": "system",
      "content": "You are a helpful assistant...",
      "created_at": "2025-01-01T00:00:00Z"
    },
    {
      "id": "uuid-2",
      "user_id": "user-uuid",
      "session_id": "chat-session-1",
      "role": "user",
      "content": "Hello!",
      "created_at": "2025-01-01T00:00:01Z"
    },
    {
      "id": "uuid-3",
      "user_id": "user-uuid",
      "session_id": "chat-session-1",
      "role": "assistant",
      "content": "Hello! How can I help you?",
      "created_at": "2025-01-01T00:00:02Z"
    }
  ]
}
```

**cURL:**
```bash
curl http://localhost:8000/api/chat/conversation/session-123/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 12. Clear Conversation

**DELETE** `/chat/conversation/<session_id>/clear/`

Delete all messages in a conversation session.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "message": "Conversation cleared successfully"
}
```

**cURL:**
```bash
curl -X DELETE http://localhost:8000/api/chat/conversation/session-123/clear/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 13. Get All User Sessions

**GET** `/chat/sessions/`

Get all conversation sessions for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "sessions": [
    {
      "session_id": "chat-session-1",
      "title": "Hello!",
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:05:00Z"
    },
    {
      "session_id": "chat-session-2",
      "title": "Tell me about cars",
      "created_at": "2025-01-02T00:00:00Z",
      "updated_at": "2025-01-02T00:10:00Z"
    }
  ]
}
```

**cURL:**
```bash
curl http://localhost:8000/api/chat/sessions/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## API Summary Table

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/auth/signup/` | POST | ❌ | Create account |
| `/auth/login/` | POST | ❌ | Login |
| `/auth/logout/` | POST | ✅ | Logout |
| `/auth/profile/` | GET | ✅ | Get profile |
| `/auth/profile/` | PATCH | ✅ | Update profile |
| `/auth/password-reset/` | POST | ❌ | Request reset |
| `/auth/password-reset/confirm/` | POST | ❌ | Confirm reset |
| `/auth/change-password/` | POST | ✅ | Change password |
| `/chat/` | POST | ✅ | Send message |
| `/chat/stream/` | POST | ✅ | Send (streaming) |
| `/chat/conversation/<id>/` | GET | ✅ | Get history |
| `/chat/conversation/<id>/clear/` | DELETE | ✅ | Clear chat |
| `/chat/sessions/` | GET | ✅ | Get all sessions |

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Email and password are required"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "error": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Something went wrong: [error details]"
}
```

---

## Authentication Flow

```
1. Signup/Login
   ↓
2. Receive access_token
   ↓
3. Store token (localStorage)
   ↓
4. Include in requests:
   Authorization: Bearer <access_token>
   ↓
5. Access protected endpoints
```

---

## Common Patterns

### Store Token (JavaScript)
```javascript
const data = await login(email, password);
localStorage.setItem('access_token', data.access_token);
```

### Get Token
```javascript
const token = localStorage.getItem('access_token');
```

### Make Authenticated Request
```javascript
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({ message: 'Hello' })
});
```

### Handle Token Expiry
```javascript
try {
  const response = await fetch(url, options);
  if (response.status === 401) {
    // Token expired - redirect to login
    window.location.href = '/login';
  }
} catch (error) {
  console.error(error);
}
```

---

## Complete Example: Full Flow

```bash
# 1. Signup
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"pass123"}'

# Response: {"access_token":"eyJ...","user":{...}}

# 2. Send Chat Message (use token from step 1)
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"message":"Hello","session_id":"test-1"}'

# Response: {"response":"Hello! How can I help?","session_id":"test-1"}

# 3. Get Conversation History
curl http://localhost:8000/api/chat/conversation/test-1/ \
  -H "Authorization: Bearer eyJ..."

# Response: {"messages":[...]}

# 4. Clear Conversation
curl -X DELETE http://localhost:8000/api/chat/conversation/test-1/clear/ \
  -H "Authorization: Bearer eyJ..."

# Response: {"message":"Conversation cleared successfully"}

# 5. Logout
curl -X POST http://localhost:8000/api/auth/logout/ \
  -H "Authorization: Bearer eyJ..."

# Response: {"message":"Logout successful"}
```

---

## Tips

1. **Always include `Content-Type: application/json`** for POST/PATCH requests
2. **Store tokens securely** (localStorage for web, secure storage for mobile)
3. **Handle 401 errors** by redirecting to login
4. **Use streaming endpoint** for better UX with long responses
5. **Clear tokens on logout** to prevent unauthorized access

---

## Testing Tools

### Postman
1. Create new collection
2. Add environment variable: `base_url = http://localhost:8000/api`
3. Add endpoints with `{{base_url}}/auth/login/`
4. Save token from login to environment
5. Use `{{token}}` in Authorization header

### cURL
See examples above for each endpoint

### Browser DevTools
```javascript
// In browser console
fetch('http://localhost:8000/api/auth/signup/', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email:'test@test.com',password:'pass123'})
}).then(r => r.json()).then(console.log)
```

---

## Need Help?

- **Backend Setup**: See `DJANGO_SETUP.md`
- **Frontend Integration**: See `FRONTEND_GUIDE.md`
- **Password Features**: See `PASSWORD_RESET_GUIDE.md`
- **Quick Start**: See `QUICKSTART.md`

Happy coding! 🚀

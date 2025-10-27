# Password Reset & Management Guide

## Overview

SafyCore Backend now includes comprehensive password management features:

1. **Password Reset** - For users who forgot their password
2. **Change Password** - For logged-in users to update their password
3. **Email-based Reset Flow** - Secure token-based password recovery

## Features Added

### 1. Request Password Reset
**Endpoint:** `POST /api/auth/password-reset/`

Sends a password reset email to the user via Supabase.

### 2. Confirm Password Reset
**Endpoint:** `POST /api/auth/password-reset/confirm/`

Completes the password reset with the token from the email.

### 3. Change Password (While Logged In)
**Endpoint:** `POST /api/auth/change-password/`

Allows authenticated users to change their password.

---

## How It Works

### Password Reset Flow

```
┌──────────┐                          ┌─────────┐                     ┌──────────┐
│  User    │                          │ Django  │                     │ Supabase │
└────┬─────┘                          └────┬────┘                     └────┬─────┘
     │                                     │                               │
     │ 1. POST /api/auth/password-reset/  │                               │
     │    {email: "user@example.com"}     │                               │
     ├────────────────────────────────────►│                               │
     │                                     │                               │
     │                                     │ 2. reset_password_email()     │
     │                                     ├──────────────────────────────►│
     │                                     │                               │
     │                                     │                               │ 3. Send email
     │                                     │                               │    with reset
     │                                     │                               │    link + token
     │                                     │                               │
     │ 4. Email received                   │                               │
     │◄────────────────────────────────────┼───────────────────────────────┤
     │                                     │                               │
     │ 5. Click link → Extract token       │                               │
     │                                     │                               │
     │ 6. POST /api/auth/password-reset/confirm/                          │
     │    {access_token: "...", new_password: "..."}                      │
     ├────────────────────────────────────►│                               │
     │                                     │                               │
     │                                     │ 7. update_user(password)      │
     │                                     ├──────────────────────────────►│
     │                                     │                               │
     │                                     │◄──────────────────────────────┤
     │                                     │   Password updated            │
     │◄────────────────────────────────────┤                               │
     │   Success message                   │                               │
     │                                     │                               │
```

---

## API Usage

### 1. Request Password Reset

**Endpoint:** `POST /api/auth/password-reset/`

**Request:**
```http
POST /api/auth/password-reset/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "Password reset email sent. Please check your inbox.",
  "email": "user@example.com"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

**Security Note:** The API always returns success even if the email doesn't exist (prevents email enumeration attacks).

---

### 2. Confirm Password Reset

**Endpoint:** `POST /api/auth/password-reset/confirm/`

**Request:**
```http
POST /api/auth/password-reset/confirm/
Content-Type: application/json

{
  "access_token": "token-from-email-link",
  "new_password": "newSecurePassword123"
}
```

**Response:**
```json
{
  "message": "Password updated successfully. You can now login with your new password."
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "eyJhbGc...",
    "new_password": "newPassword123"
  }'
```

**How to Get the Token:**

The reset email from Supabase contains a link like:
```
https://your-app.com/reset-password?access_token=eyJhbGc...&type=recovery
```

Extract the `access_token` parameter from the URL.

---

### 3. Change Password (Authenticated Users)

**Endpoint:** `POST /api/auth/change-password/`

**Requires:** Authentication (`Authorization: Bearer <token>`)

**Request:**
```http
POST /api/auth/change-password/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "oldPassword123",
  "new_password": "newSecurePassword456"
}
```

**Response (Success):**
```json
{
  "message": "Password changed successfully"
}
```

**Response (Wrong Current Password):**
```json
{
  "error": "Current password is incorrect"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "current_password": "oldPass123",
    "new_password": "newPass456"
  }'
```

---

## Frontend Integration

### Example: Password Reset Flow

```javascript
// Step 1: Request password reset
const requestPasswordReset = async (email) => {
  const response = await fetch('http://localhost:8000/api/auth/password-reset/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  const data = await response.json();
  console.log(data.message); // "Password reset email sent..."
};

// Step 2: User clicks email link and lands on your reset page
// Extract token from URL: ?access_token=xxx&type=recovery
const urlParams = new URLSearchParams(window.location.search);
const resetToken = urlParams.get('access_token');

// Step 3: Confirm password reset with new password
const confirmPasswordReset = async (token, newPassword) => {
  const response = await fetch('http://localhost:8000/api/auth/password-reset/confirm/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      access_token: token,
      new_password: newPassword
    })
  });
  const data = await response.json();
  console.log(data.message); // "Password updated successfully..."
};

// Usage
requestPasswordReset('user@example.com')
  .then(() => alert('Check your email!'));

// On reset password page:
confirmPasswordReset(resetToken, 'newPassword123')
  .then(() => alert('Password reset! You can now login.'));
```

### Example: Change Password (While Logged In)

```javascript
const changePassword = async (currentPassword, newPassword) => {
  const token = localStorage.getItem('access_token');

  const response = await fetch('http://localhost:8000/api/auth/change-password/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  });

  const data = await response.json();

  if (response.ok) {
    alert(data.message); // "Password changed successfully"
  } else {
    alert(data.error); // "Current password is incorrect"
  }
};

// Usage
changePassword('oldPass123', 'newPass456');
```

---

## Supabase Email Configuration

### Important: Configure Email Templates

1. **Go to Supabase Dashboard**
   - Navigate to: Authentication → Email Templates

2. **Configure "Reset Password" Template**

Default template:
```html
<h2>Reset Password</h2>
<p>Click the link below to reset your password:</p>
<p><a href="{{ .ConfirmationURL }}">Reset Password</a></p>
```

**Customize the URL:**

Update `{{ .ConfirmationURL }}` to point to your frontend:
```html
<p><a href="https://your-app.com/reset-password?access_token={{ .Token }}&type=recovery">
  Reset Password
</a></p>
```

3. **Configure SMTP Settings (Optional)**

For custom email domain:
- Go to: Project Settings → Auth → Email Settings
- Add your SMTP credentials

---

## Security Features

### 1. Token-Based Reset
- Tokens expire after 1 hour (Supabase default)
- Tokens are single-use (cannot be reused)
- Tokens are cryptographically secure

### 2. Email Enumeration Protection
- Always returns success message (even if email doesn't exist)
- Prevents attackers from discovering valid emails

### 3. Password Verification
- Change password requires current password
- Validates old password before allowing change
- Prevents unauthorized password changes

### 4. Rate Limiting (Supabase)
- Built-in rate limiting on auth endpoints
- Prevents brute-force attacks

---

## Testing

### Test Password Reset Flow

**1. Request Reset:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com"}'
```

**2. Check Email:**
- Go to your email inbox
- Find email from Supabase
- Click the reset link
- Extract the `access_token` from URL

**3. Reset Password:**
```bash
curl -X POST http://localhost:8000/api/auth/password-reset/confirm/ \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "YOUR_TOKEN_FROM_EMAIL",
    "new_password": "newPassword123"
  }'
```

**4. Login with New Password:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"newPassword123"}'
```

### Test Change Password

**1. Login First:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"currentPass123"}'

# Copy the access_token from response
```

**2. Change Password:**
```bash
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "current_password": "currentPass123",
    "new_password": "newPass456"
  }'
```

---

## Error Handling

### Common Errors

**1. "Email is required"**
```json
{"error": "Email is required"}
```
→ Make sure to include email in request body

**2. "Access token and new password are required"**
```json
{"error": "Access token and new password are required"}
```
→ Include both `access_token` and `new_password` in confirm request

**3. "Current password is incorrect"**
```json
{"error": "Current password is incorrect"}
```
→ User entered wrong current password in change password request

**4. "Failed to reset password: Invalid token"**
```json
{"error": "Failed to reset password: Invalid token"}
```
→ Token expired (>1 hour old) or already used

---

## UI/UX Best Practices

### Password Reset Page

```html
<!-- reset-password.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Reset Password</title>
</head>
<body>
    <h2>Reset Your Password</h2>
    <form id="resetForm">
        <input type="password" id="newPassword" placeholder="New Password" required>
        <input type="password" id="confirmPassword" placeholder="Confirm Password" required>
        <button type="submit">Reset Password</button>
    </form>

    <script>
        // Extract token from URL
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('access_token');

        if (!token) {
            alert('Invalid reset link');
        }

        document.getElementById('resetForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const newPassword = document.getElementById('newPassword').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            if (newPassword !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            const response = await fetch('http://localhost:8000/api/auth/password-reset/confirm/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    access_token: token,
                    new_password: newPassword
                })
            });

            const data = await response.json();

            if (response.ok) {
                alert(data.message);
                window.location.href = '/login'; // Redirect to login
            } else {
                alert(data.error);
            }
        });
    </script>
</body>
</html>
```

---

## Complete Endpoint List

| Endpoint | Method | Auth Required | Purpose |
|----------|--------|---------------|---------|
| `/api/auth/signup/` | POST | ❌ No | Create account |
| `/api/auth/login/` | POST | ❌ No | Login |
| `/api/auth/logout/` | POST | ✅ Yes | Logout |
| `/api/auth/profile/` | GET/PATCH | ✅ Yes | View/update profile |
| `/api/auth/password-reset/` | POST | ❌ No | Request password reset |
| `/api/auth/password-reset/confirm/` | POST | ❌ No | Confirm reset |
| `/api/auth/change-password/` | POST | ✅ Yes | Change password |

---

## Summary

✅ **Password Reset** - Email-based recovery flow
✅ **Change Password** - For logged-in users
✅ **Secure Tokens** - Expire after 1 hour
✅ **Email Protection** - Prevents enumeration
✅ **Production Ready** - Follows security best practices

Your users can now:
1. Reset forgotten passwords via email
2. Change passwords while logged in
3. Recover access to their accounts securely

All password operations are handled securely by Supabase Auth! 🔐

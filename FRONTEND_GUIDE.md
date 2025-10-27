# SafyCore Frontend Integration Guide

## Overview

This guide shows you how to build a complete frontend that integrates with the SafyCore Django backend API.

## Table of Contents

1. [Setup & Configuration](#setup--configuration)
2. [Authentication Flow](#authentication-flow)
3. [API Service Layer](#api-service-layer)
4. [React Components](#react-components)
5. [Complete Examples](#complete-examples)
6. [Best Practices](#best-practices)

---

## Setup & Configuration

### Prerequisites

- Node.js 16+ installed
- React 18+ (or any frontend framework)
- Backend running at `http://localhost:8000`

### Create React App

```bash
npx create-react-app safycore-frontend
cd safycore-frontend
npm install axios react-router-dom
npm start
```

### Project Structure

```
safycore-frontend/
├── src/
│   ├── api/
│   │   ├── auth.js          # Authentication API calls
│   │   ├── chat.js          # Chat API calls
│   │   └── config.js        # API configuration
│   ├── components/
│   │   ├── Auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── ForgotPassword.jsx
│   │   │   ├── ResetPassword.jsx
│   │   │   └── ChangePassword.jsx
│   │   ├── Chat/
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── MessageList.jsx
│   │   │   ├── MessageInput.jsx
│   │   │   └── SessionList.jsx
│   │   └── Layout/
│   │       ├── Navbar.jsx
│   │       └── ProtectedRoute.jsx
│   ├── context/
│   │   └── AuthContext.jsx   # Global auth state
│   ├── hooks/
│   │   ├── useAuth.js
│   │   └── useChat.js
│   ├── App.js
│   └── index.js
└── package.json
```

---

## API Service Layer

### 1. API Configuration (`src/api/config.js`)

```javascript
// API base URL
export const API_BASE_URL = 'http://localhost:8000/api';

// Get authorization header
export const getAuthHeader = () => {
  const token = localStorage.getItem('access_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// API client with error handling
export const apiClient = async (url, options = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
        ...options.headers,
      },
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }

    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

### 2. Authentication API (`src/api/auth.js`)

```javascript
import { apiClient, API_BASE_URL } from './config';

export const authAPI = {
  // Signup
  signup: async (email, password) => {
    const data = await apiClient('/auth/signup/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // Store tokens
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  },

  // Login
  login: async (email, password) => {
    const data = await apiClient('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // Store tokens
    if (data.access_token) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    return data;
  },

  // Logout
  logout: async () => {
    try {
      await apiClient('/auth/logout/', { method: 'POST' });
    } finally {
      // Clear local storage even if API call fails
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  },

  // Get Profile
  getProfile: async () => {
    return await apiClient('/auth/profile/', { method: 'GET' });
  },

  // Update Profile
  updateProfile: async (profileData) => {
    return await apiClient('/auth/profile/', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  },

  // Request Password Reset
  requestPasswordReset: async (email) => {
    return await apiClient('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email }),
    });
  },

  // Confirm Password Reset
  confirmPasswordReset: async (accessToken, newPassword) => {
    return await apiClient('/auth/password-reset/confirm/', {
      method: 'POST',
      body: JSON.stringify({
        access_token: accessToken,
        new_password: newPassword,
      }),
    });
  },

  // Change Password
  changePassword: async (currentPassword, newPassword) => {
    return await apiClient('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  },

  // Check if user is authenticated
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  },

  // Get current user
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
};
```

### 3. Chat API (`src/api/chat.js`)

```javascript
import { apiClient, API_BASE_URL, getAuthHeader } from './config';

export const chatAPI = {
  // Send message (non-streaming)
  sendMessage: async (message, sessionId = 'default', trainingData = null) => {
    return await apiClient('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message,
        session_id: sessionId,
        training_data: trainingData,
      }),
    });
  },

  // Send message (streaming)
  sendMessageStream: async (message, sessionId = 'default', trainingData = null, onChunk) => {
    const response = await fetch(`${API_BASE_URL}/chat/stream/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeader(),
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        training_data: trainingData,
      }),
    });

    if (!response.ok) {
      throw new Error('Stream request failed');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let fullResponse = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      fullResponse += chunk;

      if (onChunk) {
        onChunk(chunk, fullResponse);
      }
    }

    return fullResponse;
  },

  // Get conversation history
  getConversation: async (sessionId) => {
    return await apiClient(`/chat/conversation/${sessionId}/`, {
      method: 'GET',
    });
  },

  // Clear conversation
  clearConversation: async (sessionId) => {
    return await apiClient(`/chat/conversation/${sessionId}/clear/`, {
      method: 'DELETE',
    });
  },

  // Get all user sessions
  getUserSessions: async () => {
    return await apiClient('/chat/sessions/', {
      method: 'GET',
    });
  },
};
```

---

## React Components

### 1. Auth Context (`src/context/AuthContext.jsx`)

```javascript
import React, { createContext, useState, useEffect } from 'react';
import { authAPI } from '../api/auth';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on mount
    const currentUser = authAPI.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    const data = await authAPI.login(email, password);
    setUser(data.user);
    return data;
  };

  const signup = async (email, password) => {
    const data = await authAPI.signup(email, password);
    setUser(data.user);
    return data;
  };

  const logout = async () => {
    await authAPI.logout();
    setUser(null);
  };

  const value = {
    user,
    login,
    signup,
    logout,
    isAuthenticated: !!user,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

### 2. Custom Hooks

#### `src/hooks/useAuth.js`

```javascript
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

#### `src/hooks/useChat.js`

```javascript
import { useState } from 'react';
import { chatAPI } from '../api/chat';

export const useChat = (sessionId = 'default') => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);

  const sendMessage = async (message, trainingData = null) => {
    setLoading(true);

    // Add user message to UI
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await chatAPI.sendMessage(message, sessionId, trainingData);

      // Add assistant message to UI
      const assistantMessage = { role: 'assistant', content: response.response };
      setMessages(prev => [...prev, assistantMessage]);

      return response;
    } catch (error) {
      console.error('Send message error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const sendMessageStream = async (message, trainingData = null) => {
    setStreaming(true);

    // Add user message to UI
    const userMessage = { role: 'user', content: message };
    setMessages(prev => [...prev, userMessage]);

    // Add placeholder for assistant message
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

    try {
      await chatAPI.sendMessageStream(
        message,
        sessionId,
        trainingData,
        (chunk, fullResponse) => {
          // Update the last message (assistant) with streaming content
          setMessages(prev => {
            const newMessages = [...prev];
            newMessages[newMessages.length - 1].content = fullResponse;
            return newMessages;
          });
        }
      );
    } catch (error) {
      console.error('Stream error:', error);
      throw error;
    } finally {
      setStreaming(false);
    }
  };

  const loadConversation = async () => {
    setLoading(true);
    try {
      const data = await chatAPI.getConversation(sessionId);
      setMessages(data.messages || []);
    } catch (error) {
      console.error('Load conversation error:', error);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = async () => {
    try {
      await chatAPI.clearConversation(sessionId);
      setMessages([]);
    } catch (error) {
      console.error('Clear conversation error:', error);
      throw error;
    }
  };

  return {
    messages,
    loading,
    streaming,
    sendMessage,
    sendMessageStream,
    loadConversation,
    clearConversation,
  };
};
```

### 3. Login Component (`src/components/Auth/Login.jsx`)

```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Auth.css';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/chat');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Login to SafyCore</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/forgot-password">Forgot password?</Link>
          <span>•</span>
          <Link to="/signup">Create account</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
```

### 4. Signup Component (`src/components/Auth/Signup.jsx`)

```javascript
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Auth.css';

const Signup = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signup } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await signup(email, password);
      navigate('/chat');
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Create Account</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>

        <div className="auth-links">
          Already have an account? <Link to="/login">Login</Link>
        </div>
      </div>
    </div>
  );
};

export default Signup;
```

### 5. Forgot Password Component (`src/components/Auth/ForgotPassword.jsx`)

```javascript
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import './Auth.css';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await authAPI.requestPasswordReset(email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Failed to send reset email');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Check Your Email</h2>
          <p className="success-message">
            If an account exists with {email}, you will receive a password reset link.
          </p>
          <Link to="/login" className="btn-secondary">Back to Login</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Forgot Password</h2>
        <p>Enter your email and we'll send you a reset link.</p>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div className="auth-links">
          <Link to="/login">Back to Login</Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
```

### 6. Reset Password Component (`src/components/Auth/ResetPassword.jsx`)

```javascript
import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authAPI } from '../../api/auth';
import './Auth.css';

const ResetPassword = () => {
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [token, setToken] = useState('');

  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    // Get token from URL
    const accessToken = searchParams.get('access_token');
    if (!accessToken) {
      setError('Invalid reset link');
    } else {
      setToken(accessToken);
    }
  }, [searchParams]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);

    try {
      await authAPI.confirmPasswordReset(token, newPassword);
      alert('Password reset successfully! You can now login.');
      navigate('/login');
    } catch (err) {
      setError(err.message || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  if (!token) {
    return (
      <div className="auth-container">
        <div className="auth-card">
          <h2>Invalid Reset Link</h2>
          <p className="error-message">This password reset link is invalid or expired.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>Reset Password</h2>

        {error && <div className="error-message">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>New Password</label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <div className="form-group">
            <label>Confirm Password</label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Resetting...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
```

### 7. Chat Interface Component (`src/components/Chat/ChatInterface.jsx`)

```javascript
import React, { useState, useEffect } from 'react';
import { useChat } from '../../hooks/useChat';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import './Chat.css';

const ChatInterface = () => {
  const [sessionId, setSessionId] = useState('default');
  const [trainingData, setTrainingData] = useState('');
  const [showTraining, setShowTraining] = useState(false);

  const {
    messages,
    loading,
    streaming,
    sendMessage,
    sendMessageStream,
    loadConversation,
    clearConversation,
  } = useChat(sessionId);

  useEffect(() => {
    // Load conversation when component mounts
    loadConversation();
  }, [sessionId]);

  const handleSendMessage = async (message) => {
    const training = messages.length === 0 && trainingData ? trainingData : null;

    try {
      // Use streaming for better UX
      await sendMessageStream(message, training);
    } catch (error) {
      alert('Failed to send message: ' + error.message);
    }
  };

  const handleClearChat = async () => {
    if (window.confirm('Clear this conversation?')) {
      try {
        await clearConversation();
      } catch (error) {
        alert('Failed to clear conversation: ' + error.message);
      }
    }
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>SafyCore Chat</h2>
        <div className="chat-controls">
          <button onClick={() => setShowTraining(!showTraining)} className="btn-secondary">
            {showTraining ? 'Hide' : 'Show'} Training Data
          </button>
          <button onClick={handleClearChat} className="btn-danger">
            Clear Chat
          </button>
        </div>
      </div>

      {showTraining && (
        <div className="training-data-section">
          <label>Training Data (first message only):</label>
          <textarea
            value={trainingData}
            onChange={(e) => setTrainingData(e.target.value)}
            placeholder="Enter custom training data here..."
            rows="4"
          />
        </div>
      )}

      <MessageList messages={messages} loading={loading || streaming} />

      <MessageInput onSend={handleSendMessage} disabled={loading || streaming} />
    </div>
  );
};

export default ChatInterface;
```

### 8. Message List Component (`src/components/Chat/MessageList.jsx`)

```javascript
import React, { useEffect, useRef } from 'react';
import './Chat.css';

const MessageList = ({ messages, loading }) => {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="message-list">
      {messages.length === 0 && !loading && (
        <div className="empty-state">
          <p>No messages yet. Start a conversation!</p>
        </div>
      )}

      {messages
        .filter(msg => msg.role !== 'system')
        .map((message, index) => (
          <div
            key={index}
            className={`message ${message.role === 'user' ? 'user-message' : 'assistant-message'}`}
          >
            <div className="message-role">
              {message.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div className="message-content">
              {message.content}
            </div>
          </div>
        ))}

      {loading && (
        <div className="message assistant-message">
          <div className="message-role">Assistant</div>
          <div className="message-content typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;
```

### 9. Message Input Component (`src/components/Chat/MessageInput.jsx`)

```javascript
import React, { useState } from 'react';
import './Chat.css';

const MessageInput = ({ onSend, disabled }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message);
      setMessage('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="message-input">
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={disabled ? 'Sending...' : 'Type your message...'}
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !message.trim()}>
        Send
      </button>
    </form>
  );
};

export default MessageInput;
```

### 10. Protected Route Component (`src/components/Layout/ProtectedRoute.jsx`)

```javascript
import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
};

export default ProtectedRoute;
```

### 11. Navbar Component (`src/components/Layout/Navbar.jsx`)

```javascript
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import './Layout.css';

const Navbar = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">SafyCore</Link>
      </div>

      <div className="navbar-menu">
        {isAuthenticated ? (
          <>
            <Link to="/chat">Chat</Link>
            <Link to="/profile">Profile</Link>
            <span className="user-email">{user?.email}</span>
            <button onClick={handleLogout} className="btn-secondary">
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/signup">Sign Up</Link>
          </>
        )}
      </div>
    </nav>
  );
};

export default Navbar;
```

---

## Complete App Setup

### Main App Component (`src/App.js`)

```javascript
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';

// Components
import Navbar from './components/Layout/Navbar';
import ProtectedRoute from './components/Layout/ProtectedRoute';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import ForgotPassword from './components/Auth/ForgotPassword';
import ResetPassword from './components/Auth/ResetPassword';
import ChatInterface from './components/Chat/ChatInterface';

import './App.css';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="app">
          <Navbar />

          <div className="app-content">
            <Routes>
              <Route path="/" element={<Navigate to="/chat" replace />} />

              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />

              {/* Protected routes */}
              <Route
                path="/chat"
                element={
                  <ProtectedRoute>
                    <ChatInterface />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </div>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
```

---

## CSS Styles

### Auth Styles (`src/components/Auth/Auth.css`)

```css
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.auth-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 40px;
  max-width: 400px;
  width: 100%;
}

.auth-card h2 {
  margin-bottom: 24px;
  color: #333;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #6c5ce7;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background: #6c5ce7;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background: #5f4fd1;
}

.btn-primary:disabled {
  background: #a29bdb;
  cursor: not-allowed;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.success-message {
  background: #efe;
  color: #3c3;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 20px;
  font-size: 14px;
}

.auth-links {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.auth-links a {
  color: #6c5ce7;
  text-decoration: none;
  font-weight: 500;
}

.auth-links a:hover {
  text-decoration: underline;
}

.auth-links span {
  margin: 0 8px;
}
```

### Chat Styles (`src/components/Chat/Chat.css`)

```css
.chat-interface {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 80px);
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #6c5ce7;
  color: white;
}

.chat-header h2 {
  margin: 0;
}

.chat-controls {
  display: flex;
  gap: 10px;
}

.btn-secondary {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.3);
}

.btn-danger {
  padding: 8px 16px;
  background: #ff4757;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.btn-danger:hover {
  background: #ee2f40;
}

.training-data-section {
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.training-data-section label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.training-data-section textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: monospace;
  font-size: 14px;
  resize: vertical;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f8f9fa;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-size: 18px;
}

.message {
  margin-bottom: 20px;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #666;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  max-width: 70%;
}

.user-message .message-content {
  background: #6c5ce7;
  color: white;
  margin-left: auto;
}

.assistant-message .message-content {
  background: white;
  color: #333;
  border: 1px solid #ddd;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 16px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-10px); }
}

.message-input {
  display: flex;
  gap: 10px;
  padding: 20px;
  background: white;
  border-top: 1px solid #ddd;
}

.message-input input {
  flex: 1;
  padding: 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
}

.message-input input:focus {
  outline: none;
  border-color: #6c5ce7;
}

.message-input button {
  padding: 14px 32px;
  background: #6c5ce7;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.message-input button:hover:not(:disabled) {
  background: #5f4fd1;
}

.message-input button:disabled {
  background: #a29bdb;
  cursor: not-allowed;
}
```

### Layout Styles (`src/components/Layout/Layout.css`)

```css
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 32px;
  background: #2d3436;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand a {
  font-size: 24px;
  font-weight: 700;
  color: white;
  text-decoration: none;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 24px;
}

.navbar-menu a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.navbar-menu a:hover {
  opacity: 0.8;
}

.user-email {
  color: #b2bec3;
  font-size: 14px;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 24px;
  color: #666;
}
```

### Main App Styles (`src/App.css`)

```css
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f5f6fa;
}

.app {
  min-height: 100vh;
}

.app-content {
  padding: 20px;
}
```

---

## Running the Frontend

### 1. Install Dependencies

```bash
cd safycore-frontend
npm install
```

### 2. Update Package.json

Add proxy for development (optional):

```json
{
  "proxy": "http://localhost:8000",
  ...
}
```

### 3. Start Development Server

```bash
npm start
```

Frontend will run at: `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

---

## Testing the Integration

### 1. Start Backend

```bash
py manage.py runserver
```

### 2. Start Frontend

```bash
npm start
```

### 3. Test Flow

1. **Sign Up**: Go to `http://localhost:3000/signup`
2. **Login**: After signup, you'll be redirected to chat
3. **Send Message**: Type a message and press send
4. **See Streaming**: Watch the response stream in real-time
5. **Test Password Reset**: Logout → Forgot Password → Check email

---

## Best Practices

### 1. Error Handling

```javascript
try {
  const data = await authAPI.login(email, password);
  // Success
} catch (error) {
  // Show user-friendly error message
  setError(error.message || 'Something went wrong');
}
```

### 2. Loading States

```javascript
const [loading, setLoading] = useState(false);

// Show loading indicator
{loading && <div className="loading-spinner">Loading...</div>}
```

### 3. Token Refresh

Add token refresh logic:

```javascript
// In api/config.js
export const refreshToken = async () => {
  const refresh = localStorage.getItem('refresh_token');
  // Call refresh endpoint (you'd need to implement this)
  const response = await fetch('/api/auth/refresh/', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refresh }),
  });
  const data = await response.json();
  localStorage.setItem('access_token', data.access_token);
};
```

### 4. Environment Variables

Create `.env`:

```env
REACT_APP_API_URL=http://localhost:8000/api
```

Use in code:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
```

---

## Deployment

### Deploy Frontend (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd safycore-frontend
vercel
```

### Update API URL

In production, update `API_BASE_URL` to your Django backend URL:

```javascript
export const API_BASE_URL = 'https://your-django-backend.com/api';
```

---

## Summary

You now have:

✅ Complete React frontend with all API integrations
✅ Authentication flow (signup, login, logout, password reset)
✅ Chat interface with streaming support
✅ Protected routes
✅ Error handling
✅ Beautiful UI with CSS
✅ Production-ready code

**Start the apps and test the full flow!** 🚀

For questions or issues, refer to:
- `DJANGO_SETUP.md` - Backend setup
- `PASSWORD_RESET_GUIDE.md` - Password features
- This file - Frontend integration

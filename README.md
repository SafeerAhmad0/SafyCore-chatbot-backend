# SafyCore Chatbot API

A fast, production-ready chatbot API using Groq's AI models with conversation history management.

## Features

- **Fast Responses**: Conversation history stored in backend (no repeated API calls)
- **Streaming Support**: Real-time token-by-token responses for better UX
- **Session Management**: Multiple conversations with unique session IDs
- **Custom Training Data**: Inject custom context/knowledge into the chatbot
- **CORS Enabled**: Ready for frontend integration

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file (or edit the existing one):

```env
GROQ_API_KEY=your_groq_api_key_here
```

Get your API key from: https://console.groq.com/keys

### 3. Run the Server

```bash
python app.py
```

The API will be available at: `http://localhost:8000`

### 4. Test the API

Open `frontend_example.html` in your browser to test the chatbot UI.

## API Endpoints

### `POST /chat`
Non-streaming chat (returns complete response at once)

**Request:**
```json
{
  "message": "Hello, how are you?",
  "session_id": "user123",
  "api_key": "optional_groq_key",
  "training_data": "Optional custom context data"
}
```

**Response:**
```json
{
  "response": "I'm doing well, thank you! How can I help you?",
  "session_id": "user123"
}
```

### `POST /chat/stream`
Streaming chat (returns response token by token)

Same request format as `/chat`, but streams the response as plain text.

### `GET /conversation/{session_id}`
Get conversation history for a session

### `DELETE /conversation/{session_id}`
Clear conversation history for a session

### `POST /train`
Update training data for a session

## How It Works (Speed Optimization)

### Backend Approach (Implemented)
1. **First message**: User sends message + training data
2. **Backend stores**: Conversation history in memory with session_id
3. **Subsequent messages**: Only new message sent, backend manages full context
4. **Result**: Fast responses, no redundant data transfer

### Why This Is Fast

- **No repeated context**: Training data sent only once
- **Session memory**: Full conversation stored on backend
- **Streaming**: Appears faster with real-time token delivery
- **Efficient API calls**: Only necessary data sent to Groq

## Frontend Integration Options

### Option 1: Use Provided HTML Example
Simply open `frontend_example.html` and enter your Groq API key.

### Option 2: React/Vue/Angular Integration

```javascript
// Example fetch call
async function sendMessage(message, sessionId) {
  const response = await fetch('http://localhost:8000/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message: message,
      session_id: sessionId,
      training_data: yourTrainingData // Only on first message
    })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    // Update UI with chunk
  }
}
```

## Training Data

Edit `training_data.txt` with your custom context:

```text
Company: YourCompany
Products: Product1, Product2
FAQs:
- Q: What is your refund policy?
  A: 30-day money back guarantee
```

The chatbot will use this information to answer questions accurately.

## Production Deployment

For production, replace in-memory storage with:
- **Redis** for session management
- **Database** for persistent conversation history
- **Environment-based CORS** (restrict origins)

## Model Options

Available Groq models (update in `app.py`):
- `openai/gpt-oss-20b` (current)
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma-7b-it`

## Troubleshooting

**Error: GROQ_API_KEY not provided**
- Add API key to `.env` file OR pass it in request body

**CORS errors**
- Update `allow_origins` in `app.py` to match your frontend URL

**Slow responses**
- Use streaming endpoint `/chat/stream` for better perceived speed
- Consider using faster Groq models like `llama-3.1-8b-instant`

## License

MIT

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from groq import Groq
from typing import List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SafyCore Chatbot API")

# CORS middleware for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation storage (use Redis/DB for production)
conversations = {}

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"
    api_key: Optional[str] = None
    training_data: Optional[str] = None
    use_streaming: Optional[bool] = True

class ChatResponse(BaseModel):
    response: str
    session_id: str

def get_system_prompt(training_data: Optional[str] = None) -> str:
    """Generate system prompt with optional training data"""
    base_prompt = """You are a car sales assistant. CRITICAL RULES:
1. ONLY answer questions using the car data provided below
2. If asked about something NOT in the data, say "I only have information about the cars listed"
3. Answer in plain text, NO markdown, NO tables, NO bullets, NO formatting (no **, *, _, |)
4. Keep answers SHORT (1-2 sentences max)
5. Be conversational and helpful"""
    if training_data:
        return f"{base_prompt}\n\nCAR DATA:\n{training_data}"
    return base_prompt

def get_groq_client(api_key: Optional[str] = None):
    """Initialize Groq client with API key from request or environment"""
    key = api_key or os.getenv("GROQ_API_KEY")
    if not key:
        raise HTTPException(
            status_code=400,
            detail="GROQ_API_KEY not provided in request or environment variables"
        )
    # Simple initialization - just pass api_key
    return Groq(api_key=key)

@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Non-streaming chat endpoint - returns complete response at once
    Faster for short responses, better for simple integrations
    """
    try:
        client = get_groq_client(request.api_key)

        # Initialize or retrieve conversation history
        if request.session_id not in conversations:
            conversations[request.session_id] = []

        # Add system prompt with training data if this is first message
        if len(conversations[request.session_id]) == 0 and request.training_data:
            conversations[request.session_id].append({
                "role": "system",
                "content": get_system_prompt(request.training_data)
            })

        # Add user message to conversation history
        conversations[request.session_id].append({
            "role": "user",
            "content": request.message
        })

        # Get completion from Groq
        completion = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=conversations[request.session_id],
            temperature=0.3,
            max_completion_tokens=100,
            top_p=0.9,
            stream=False
        )

        assistant_message = completion.choices[0].message.content

        # Strip ALL markdown formatting
        import re
        assistant_message = re.sub(r'\*\*([^*]+)\*\*', r'\1', assistant_message)  # Remove bold
        assistant_message = re.sub(r'\*([^*]+)\*', r'\1', assistant_message)      # Remove italic
        assistant_message = re.sub(r'__([^_]+)__', r'\1', assistant_message)      # Remove bold underscore
        assistant_message = re.sub(r'_([^_]+)_', r'\1', assistant_message)        # Remove italic underscore
        assistant_message = re.sub(r'\|.*\|', '', assistant_message)              # Remove table rows
        assistant_message = re.sub(r'^[-=]+$', '', assistant_message, flags=re.MULTILINE)  # Remove separators
        assistant_message = re.sub(r'^\s*[-*+]\s+', '', assistant_message, flags=re.MULTILINE)  # Remove bullets
        assistant_message = re.sub(r'^\s*\d+\.\s+', '', assistant_message, flags=re.MULTILINE)  # Remove numbered lists
        assistant_message = assistant_message.strip()

        # Add assistant response to conversation history
        conversations[request.session_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        return ChatResponse(
            response=assistant_message,
            session_id=request.session_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Streaming chat endpoint - returns response token by token
    Better UX for long responses, feels more responsive
    """
    try:
        client = get_groq_client(request.api_key)

        # Initialize or retrieve conversation history
        if request.session_id not in conversations:
            conversations[request.session_id] = []

        # Add system prompt with training data if this is first message
        if len(conversations[request.session_id]) == 0 and request.training_data:
            conversations[request.session_id].append({
                "role": "system",
                "content": get_system_prompt(request.training_data)
            })

        # Add user message to conversation history
        conversations[request.session_id].append({
            "role": "user",
            "content": request.message
        })

        async def generate():
            import re
            full_response = ""
            completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=conversations[request.session_id],
                temperature=0.3,
                max_completion_tokens=100,
                top_p=0.9,
                stream=True
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                yield content

            # Strip ALL markdown formatting from full response
            cleaned_response = re.sub(r'\*\*([^*]+)\*\*', r'\1', full_response)
            cleaned_response = re.sub(r'\*([^*]+)\*', r'\1', cleaned_response)
            cleaned_response = re.sub(r'__([^_]+)__', r'\1', cleaned_response)
            cleaned_response = re.sub(r'_([^_]+)_', r'\1', cleaned_response)
            cleaned_response = re.sub(r'\|.*\|', '', cleaned_response)
            cleaned_response = re.sub(r'^[-=]+$', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'^\s*[-*+]\s+', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = re.sub(r'^\s*\d+\.\s+', '', cleaned_response, flags=re.MULTILINE)
            cleaned_response = cleaned_response.strip()

            # Save cleaned response to conversation history
            conversations[request.session_id].append({
                "role": "assistant",
                "content": cleaned_response
            })

        return StreamingResponse(generate(), media_type="text/plain")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversation/{session_id}")
async def get_conversation(session_id: str):
    """Get conversation history for a session"""
    if session_id not in conversations:
        return {"messages": []}
    return {"messages": conversations[session_id]}

@app.delete("/conversation/{session_id}")
async def clear_conversation(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversations:
        del conversations[session_id]
    return {"message": "Conversation cleared"}

@app.post("/train")
async def set_training_data(session_id: str, training_data: str):
    """
    Set or update training data for a session
    This will be prepended as system message
    """
    if session_id not in conversations:
        conversations[session_id] = []

    # Update or add system message
    system_message = {
        "role": "system",
        "content": get_system_prompt(training_data)
    }

    if len(conversations[session_id]) > 0 and conversations[session_id][0]["role"] == "system":
        conversations[session_id][0] = system_message
    else:
        conversations[session_id].insert(0, system_message)

    return {"message": "Training data updated"}

@app.get("/training-data")
async def get_training_data():
    """
    Serve the training data text file
    This fixes CORS issues when loading from file system
    """
    try:
        with open("training_data.txt", "r", encoding="utf-8") as f:
            content = f.read()
        return {"training_data": content}
    except FileNotFoundError:
        return {"training_data": None}

@app.get("/")
async def root():
    return {
        "message": "SafyCore Chatbot API",
        "endpoints": {
            "POST /chat": "Non-streaming chat",
            "POST /chat/stream": "Streaming chat",
            "GET /conversation/{session_id}": "Get conversation history",
            "DELETE /conversation/{session_id}": "Clear conversation",
            "POST /train": "Set training data",
            "GET /training-data": "Get training data file"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

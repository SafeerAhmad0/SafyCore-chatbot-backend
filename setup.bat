@echo off
echo ========================================
echo SafyCore Chatbot - Setup Script
echo ========================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Checking .env file...
if not exist .env (
    echo GROQ_API_KEY=your_api_key_here > .env
    echo Created .env file - Please add your Groq API key!
) else (
    echo .env file already exists
)

echo.
echo [3/3] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo 1. Add your Groq API key to .env file
echo 2. Run: python app.py
echo 3. Open frontend_example.html in browser
echo ========================================
pause

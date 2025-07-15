#!/usr/bin/env python3
"""
Startup script for the AI Resume Assistant API
"""

import os
import sys
import uvicorn
from config import settings

def main():
    """Start the FastAPI application"""
    print("🚀 Starting AI Resume Assistant API...")
    
    # Validate settings
    try:
        settings.validate()
        print("✅ Configuration validated")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your environment variables and .env file")
        sys.exit(1)
    
    # Set up environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = settings.DEBUG
    
    print(f"📡 Server will run on {host}:{port}")
    print(f"🔧 Debug mode: {reload}")
    print(f"🤖 LLM Model: {settings.LLM_MODEL}")
    
    if settings.LLM_API_KEY == "your-openrouter-api-key":
        print("⚠️  Warning: LLM_API_KEY not set. LLM features will use fallback responses.")
    
    print("\n" + "=" * 50)
    print("🎯 API Endpoints:")
    print("   POST /start_session     - Start resume analysis")
    print("   POST /answer_question   - Submit answer")
    print("   GET  /session/{id}      - Get session status")
    print("   DELETE /session/{id}    - Delete session")
    print("   GET  /                  - API info")
    print("=" * 50)
    print("📖 API docs: http://localhost:8000/docs")
    print("🔍 Interactive docs: http://localhost:8000/redoc")
    print("=" * 50)
    
    # Start the server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info" if reload else "warning"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
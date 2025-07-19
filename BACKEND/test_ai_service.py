#!/usr/bin/env python3
"""
Test script to debug AI service issues
"""

import asyncio
import logging
from services.ai_service import ai_service
from config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)

async def test_ai_service():
    """Test the AI service to see what's happening"""
    print("Testing AI Service...")
    print(f"API URL: {settings.LLM_API_URL}")
    print(f"Model: {settings.LLM_MODEL}")
    print(f"API Key: {settings.LLM_API_KEY[:10] if settings.LLM_API_KEY else 'None'}...")
    
    # Test with a simple prompt
    test_resume = """
    \\section{Experience}
    \\resumeSubheading{Software Engineer}{Tech Corp}{Senior Developer}{2020-2023}
    \\resumeItem{Built web applications using Python and Django}
    \\resumeItem{Improved performance by 40\% through database optimization}
    """
    
    test_job = "Looking for a Python developer with Django experience and database optimization skills."
    
    try:
        # Test parsing
        print("\n1. Testing resume parsing...")
        parsed = ai_service.parse_resume_latex(test_resume)
        print(f"Parsed resume: {parsed}")
        
        # Test suggestions generation
        print("\n2. Testing suggestions generation...")
        suggestions = await ai_service.generate_structured_suggestions(
            parsed, 
            test_job, 
            ["What specific projects did you work on?"], 
            ["I built a customer portal that served 10,000 users"]
        )
        print(f"Generated suggestions: {suggestions}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ai_service()) 
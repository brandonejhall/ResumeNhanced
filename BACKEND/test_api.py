#!/usr/bin/env python3
"""
Test script for the AI Resume Assistant API
"""

import asyncio
import httpx
import json

# Sample data for testing
SAMPLE_RESUME = r"""
\documentclass{article}
\begin{document}
\title{John Doe - Software Engineer}
\author{John Doe}
\date{}

\section{Experience}
\textbf{Software Engineer} - Tech Corp (2020-2023)
\begin{itemize}
\item Developed web applications using Python and Django
\item Collaborated with cross-functional teams
\end{itemize}

\section{Skills}
\begin{itemize}
\item Python, JavaScript, SQL
\item Django, React, PostgreSQL
\end{itemize}
\end{document}
"""

SAMPLE_JOB_POST = """
We are looking for a Senior Software Engineer with:
- 5+ years of experience in Python development
- Experience with microservices architecture
- Strong background in cloud technologies (AWS/Azure)
- Experience leading technical projects
- Excellent communication skills
"""

async def test_api():
    """Test the API endpoints"""
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient() as client:
        print("🚀 Testing AI Resume Assistant API")
        print("=" * 50)
        
        # Test 1: Start session
        print("\n1. Testing /session/start...")
        start_data = {
            "resume_text": SAMPLE_RESUME,
            "job_post": SAMPLE_JOB_POST
        }
        
        try:
            response = await client.post(f"{base_url}/session/start", json=start_data)
            if response.status_code == 200:
                session_data = response.json()
                session_id = session_data["session_id"]
                questions = session_data["questions"]
                print(f"✅ Session created: {session_id}")
                print(f"📝 Questions generated: {len(questions)}")
                for i, q in enumerate(questions, 1):
                    print(f"   Q{i}: {q}")
            else:
                print(f"❌ Failed to start session: {response.status_code}")
                return
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return
        
        # Test 2: Answer questions
        print("\n2. Testing /session/answer...")
        sample_answers = [
            "I have 5 years of experience with Python, including Django and Flask frameworks. I've built several production applications handling thousands of users.",
            "In my most recent role, I increased application performance by 40% through database optimization and implemented CI/CD pipelines that reduced deployment time by 60%.",
            "I led a team of 4 developers to build a microservices architecture that processed 1M+ transactions daily. We used AWS services including Lambda, SQS, and RDS."
        ]
        
        for i, answer in enumerate(sample_answers):
            print(f"\n   Answering question {i+1}...")
            answer_data = {
                "session_id": session_id,
                "answer": answer
            }
            
            try:
                response = await client.post(f"{base_url}/session/answer", json=answer_data)
                if response.status_code == 200:
                    result = response.json()
                    if result["is_complete"]:
                        print("✅ All questions answered! Resume updated.")
                        print(f"📄 Updated resume length: {len(result['updated_resume'])} characters")
                        break
                    else:
                        print(f"✅ Answer submitted. Next question: {result['next_question'][:50]}...")
                else:
                    print(f"❌ Failed to submit answer: {response.status_code}")
                    break
            except Exception as e:
                print(f"❌ Error submitting answer: {e}")
                break
        
        # Test 3: Get session status
        print("\n3. Testing /session/{session_id}...")
        try:
            response = await client.get(f"{base_url}/session/{session_id}")
            if response.status_code == 200:
                status = response.json()
                print(f"✅ Session status retrieved")
                print(f"   Progress: {status['progress']}")
                print(f"   Created: {status['created_at']}")
            else:
                print(f"❌ Failed to get session status: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting session status: {e}")
        
        # Test 4: Root endpoint
        print("\n4. Testing / (root endpoint)...")
        try:
            response = await client.get(f"{base_url}/")
            if response.status_code == 200:
                root_data = response.json()
                print(f"✅ API info: {root_data['message']} v{root_data['version']}")
            else:
                print(f"❌ Failed to get root endpoint: {response.status_code}")
        except Exception as e:
            print(f"❌ Error getting root endpoint: {e}")
        
        # Test 5: Health check
        print("\n5. Testing /health...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check: {health_data['status']}")
            else:
                print(f"❌ Failed health check: {response.status_code}")
        except Exception as e:
            print(f"❌ Error health check: {e}")
        
        print("\n" + "=" * 50)
        print("🎉 API testing completed!")

if __name__ == "__main__":
    asyncio.run(test_api()) 
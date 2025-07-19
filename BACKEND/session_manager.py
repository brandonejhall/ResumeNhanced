"""
Session management for the resume assistant
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException

# Try to use Redis, fallback to in-memory storage
try:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # Test Redis connection
    r.ping()
    USE_REDIS = True
    print("✅ Redis connection successful - using Redis for session storage")
except (ImportError, redis.ConnectionError, Exception) as e:
    print(f"⚠️ Redis not available ({e}) - falling back to in-memory storage")
    USE_REDIS = False
    sessions = {}

class SessionManager:
    """Manages session storage and operations using Redis with fallback to in-memory"""
    
    def create_session(self, resume_text: str, job_post: str, questions: List[str]) -> str:
        session_id = str(uuid.uuid4())
        session_data = {
            "resume_text": resume_text,
            "job_post": job_post,
            "questions": questions,
            "answers": [],
            "current_question_index": 0,
            "created_at": datetime.now().isoformat()
        }
        
        if USE_REDIS:
            r.set(session_id, json.dumps(session_data))
            r.expire(session_id, 3600)  # 1 hour expiration
        else:
            sessions[session_id] = session_data
            
        return session_id
    
    def get_session(self, session_id: str) -> dict:
        if USE_REDIS:
            session_json = r.get(session_id)
            if not session_json:
                raise HTTPException(status_code=404, detail="Session not found")
            return json.loads(session_json)
        else:
            if session_id not in sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            return sessions[session_id]
    
    def add_answer(self, session_id: str, answer: str) -> dict:
        session = self.get_session(session_id)
        session["answers"].append(answer)
        
        if USE_REDIS:
            r.set(session_id, json.dumps(session))
        else:
            sessions[session_id] = session
            
        return session
    
    def is_complete(self, session: dict) -> bool:
        return len(session["answers"]) >= len(session["questions"])
    
    def get_next_question(self, session: dict) -> Optional[str]:
        if self.is_complete(session):
            return None
        return session["questions"][len(session["answers"])]
    
    def get_session_status(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        return {
            "session_id": session_id,
            "questions": session["questions"],
            "answers": session["answers"],
            "current_question": self.get_next_question(session),
            "progress": f"{len(session['answers'])}/{len(session['questions'])}",
            "created_at": session["created_at"]
        }
    
    def delete_session(self, session_id: str) -> None:
        if USE_REDIS:
            if not r.delete(session_id):
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            if session_id not in sessions:
                raise HTTPException(status_code=404, detail="Session not found")
            del sessions[session_id]

    def cleanup_session(self, session_id: str) -> None:
        if USE_REDIS:
            r.delete(session_id)
        else:
            if session_id in sessions:
                del sessions[session_id]

    def _set_session(self, session_id: str, session_data: dict) -> None:
        if USE_REDIS:
            r.set(session_id, json.dumps(session_data))
            r.expire(session_id, 3600)
        else:
            sessions[session_id] = session_data

    def get_suggestions(self, session_id: str):
        session = self.get_session(session_id)
        import json
        from models import Suggestion
        suggestions_json = session.get('suggestions', '[]')
        return [Suggestion(**s) for s in json.loads(suggestions_json)]

# Global session manager instance
session_manager = SessionManager() 
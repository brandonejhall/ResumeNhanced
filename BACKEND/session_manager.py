"""
Session management for the resume assistant
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import HTTPException

class SessionManager:
    """Manages session storage and operations"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}
    
    def create_session(self, resume_text: str, job_post: str, questions: List[str]) -> str:
        """Create a new session and return session ID"""
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "resume_text": resume_text,
            "job_post": job_post,
            "questions": questions,
            "answers": [],
            "current_question_index": 0,
            "created_at": datetime.now().isoformat()
        }
        
        return session_id
    
    def get_session(self, session_id: str) -> Dict:
        """Get session data by ID"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        return self.sessions[session_id]
    
    def add_answer(self, session_id: str, answer: str) -> Dict:
        """Add an answer to a session and return session data"""
        session = self.get_session(session_id)
        session["answers"].append(answer)
        return session
    
    def is_complete(self, session: Dict) -> bool:
        """Check if all questions are answered"""
        return len(session["answers"]) >= len(session["questions"])
    
    def get_next_question(self, session: Dict) -> Optional[str]:
        """Get the next question to answer"""
        if self.is_complete(session):
            return None
        return session["questions"][len(session["answers"])]
    
    def get_session_status(self, session_id: str) -> Dict:
        """Get comprehensive session status"""
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
        """Delete a session"""
        if session_id not in self.sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        del self.sessions[session_id]
    
    def cleanup_session(self, session_id: str) -> None:
        """Clean up session after completion"""
        if session_id in self.sessions:
            del self.sessions[session_id]

# Global session manager instance
session_manager = SessionManager() 
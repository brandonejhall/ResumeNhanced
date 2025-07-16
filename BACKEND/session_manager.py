"""
Session management for the resume assistant
"""

import uuid
import json
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException
import redis

# Connect to Redis (adjust host/port/db as needed)
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class SessionManager:
    """Manages session storage and operations using Redis"""

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
        r.set(session_id, json.dumps(session_data))
        # Optionally set an expiration (e.g., 1 hour)
        r.expire(session_id, 3600)
        return session_id

    def get_session(self, session_id: str) -> dict:
        session_json = r.get(session_id)
        if not session_json:
            raise HTTPException(status_code=404, detail="Session not found")
        return json.loads(session_json)

    def add_answer(self, session_id: str, answer: str) -> dict:
        session = self.get_session(session_id)
        session["answers"].append(answer)
        r.set(session_id, json.dumps(session))
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
        if not r.delete(session_id):
            raise HTTPException(status_code=404, detail="Session not found")

    def cleanup_session(self, session_id: str) -> None:
        r.delete(session_id)

# Global session manager instance
session_manager = SessionManager() 
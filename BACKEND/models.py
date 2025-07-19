"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class StartSessionRequest(BaseModel):
    """Request model for starting a new session"""
    resume_text: str
    job_post: str

class StartSessionResponse(BaseModel):
    """Response model for session start"""
    session_id: str
    first_question: str
    total_questions: int

class AnswerQuestionRequest(BaseModel):
    """Request model for answering a question"""
    session_id: str
    answer: str

class AnswerQuestionResponse(BaseModel):
    """Response model for question answers"""
    next_question: Optional[str]
    updated_resume: Optional[str]
    is_complete: bool

class SessionStatusResponse(BaseModel):
    """Response model for session status"""
    session_id: str
    questions: List[str]
    answers: List[str]
    current_question: Optional[str]
    progress: str
    created_at: str

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str

class DeleteSessionResponse(BaseModel):
    """Response model for session deletion"""
    message: str

class RootResponse(BaseModel):
    """Root endpoint response model"""
    message: str
    version: str
    endpoints: dict 

class Suggestion(BaseModel):
    id: str  # UUID as string
    type: str  # e.g., 'replace_section', 'add_item_to_section', etc.
    target_section_header: str
    context_text_before: str
    context_text_after: str
    original_latex_snippet: str = ""
    suggested_latex_snippet: str
    description: str

class SuggestionListResponse(BaseModel):
    session_id: str
    suggestions: list[Suggestion]

class ApplySuggestionRequest(BaseModel):
    suggestion_id: str
    resume_latex: str

class ApplySuggestionResponse(BaseModel):
    updated_resume_latex: str
    suggestions: list[Suggestion] 
"""
Session router for session management endpoints
"""

from fastapi import APIRouter, HTTPException
from models import StartSessionRequest, StartSessionResponse, AnswerQuestionRequest, AnswerQuestionResponse
from session_manager import session_manager
from services.ai_service import ai_service

router = APIRouter(prefix="/session", tags=["sessions"])

@router.post("/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new resume analysis session"""
    try:
        # Generate targeted questions using AI service
        questions = await ai_service.analyze_resume_and_job(
            request.resume_text, 
            request.job_post
        )
        # Create session
        session_id = session_manager.create_session(
            request.resume_text,
            request.job_post,
            questions
        )
        return StartSessionResponse(
            session_id=session_id,
            first_question=questions[0],
            total_questions=len(questions)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting session: {str(e)}")

@router.post("/answer", response_model=AnswerQuestionResponse)
async def answer_question(request: AnswerQuestionRequest):
    """Submit an answer to the current question"""
    try:
        # Add answer to session
        session = session_manager.add_answer(request.session_id, request.answer)
        
        # Check if all questions are answered
        if len(session["answers"]) >= len(session["questions"]):
            # All questions answered, enhance resume
            updated_resume = await ai_service.enhance_resume(
                session["resume_text"],
                session["job_post"],
                session["questions"],
                session["answers"]
            )
            
            
            # Clean up session
            session_manager.cleanup_session(request.session_id)
            
            return AnswerQuestionResponse(
                next_question=None,
                updated_resume=updated_resume,
                is_complete=True
            )
        else:
            # Return next question
            next_question = session["questions"][len(session["answers"])]
            return AnswerQuestionResponse(
                next_question=next_question,
                updated_resume=None,
                is_complete=False
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")

@router.get("/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status"""
    try:
        return session_manager.get_session_status(session_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting session status: {str(e)}")

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        session_manager.delete_session(session_id)
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}") 
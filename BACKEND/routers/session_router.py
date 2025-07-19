"""
Session router for session management endpoints
"""

from fastapi import APIRouter, HTTPException
from models import StartSessionRequest, StartSessionResponse, AnswerQuestionRequest, AnswerQuestionResponse, Suggestion, SuggestionListResponse, ApplySuggestionRequest, ApplySuggestionResponse
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
            
            # Don't clean up session - keep it for suggestions
            # session_manager.cleanup_session(request.session_id)
            
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

@router.post("/suggestions", response_model=SuggestionListResponse)
async def get_suggestions(request: StartSessionRequest):
    """DEPRECATED: Generate structured AI suggestions for the resume and job post."""
    try:
        # Parse resume
        parsed_resume = ai_service.parse_resume_latex(request.resume_text)
        
        # For now, we'll create a new session and require Q&A completion
        # In a real implementation, you'd want to pass session_id and check completion
        session_id = session_manager.create_session(request.resume_text, request.job_post, [])
        
        # Generate suggestions using LLM with Q&A context
        # For now, we'll use empty Q&A to demonstrate the structure
        # In production, you'd get questions/answers from an existing session
        questions = [
            "Can you provide specific examples of your experience with the key skills mentioned in the job posting?",
            "What measurable results or metrics did you achieve in your most recent role?",
            "Describe a challenging project you led that demonstrates your ability to handle the responsibilities mentioned in this role."
        ]
        answers = [
            "I have experience with Python, Django, and AWS. I built a web application that served 10,000+ users.",
            "I increased application performance by 40% through database optimization and reduced deployment time by 60%.",
            "I led a team of 4 developers to build a microservices architecture that processed 1M+ transactions daily."
        ]
        
        suggestions = await ai_service.generate_structured_suggestions(
            parsed_resume, 
            request.job_post, 
            questions, 
            answers
        )
        
        # Store suggestions in session
        import json
        session = session_manager.get_session(session_id)
        session['suggestions'] = json.dumps([s.dict() for s in suggestions])
        session_manager._set_session(session_id, session)
        
        # Return session_id in response
        return {"session_id": session_id, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.post("/suggestions/{session_id}", response_model=SuggestionListResponse)
async def get_suggestions_for_session(session_id: str):
    """Generate structured AI suggestions for an existing session after Q&A completion."""
    try:
        # Get existing session
        session = session_manager.get_session(session_id)
        
        # Check if Q&A is complete
        if len(session["answers"]) < len(session["questions"]):
            raise HTTPException(
                status_code=400, 
                detail="Q&A session not complete. Please answer all questions before requesting suggestions."
            )
        
        # Parse resume
        parsed_resume = ai_service.parse_resume_latex(session["resume_text"])
        
        # Generate suggestions using LLM with Q&A context
        suggestions = await ai_service.generate_structured_suggestions(
            parsed_resume, 
            session["job_post"], 
            session["questions"], 
            session["answers"]
        )
        
        # Store suggestions in session
        import json
        session['suggestions'] = json.dumps([s.dict() for s in suggestions])
        session_manager._set_session(session_id, session)
        
        # Return session_id in response
        return {"session_id": session_id, "suggestions": suggestions}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.post("/apply_suggestion/{session_id}", response_model=ApplySuggestionResponse)
async def apply_suggestion(session_id: str, req: ApplySuggestionRequest):
    """Apply a single suggestion to the resume in the session."""
    try:
        import json
        session = session_manager.get_session(session_id)
        suggestions = [Suggestion(**s) for s in json.loads(session.get('suggestions', '[]'))]
        suggestion = next((s for s in suggestions if s.id == req.suggestion_id), None)
        if not suggestion:
            raise HTTPException(status_code=404, detail="Suggestion not found")
        parsed_resume = ai_service.parse_resume_latex(req.resume_latex)
        updated_parsed = ai_service.apply_suggestion(parsed_resume, suggestion)
        updated_resume = ai_service.serialize_resume_latex(updated_parsed)
        # Remove applied suggestion
        remaining = [s for s in suggestions if s.id != req.suggestion_id]
        session['suggestions'] = json.dumps([s.dict() for s in remaining])
        session['resume_text'] = updated_resume
        return ApplySuggestionResponse(
            updated_resume_latex=updated_resume,
            suggestions=remaining
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying suggestion: {str(e)}")

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
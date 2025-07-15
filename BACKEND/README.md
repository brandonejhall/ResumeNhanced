# AI Resume Assistant Backend

A FastAPI backend for an AI-powered resume assistant that analyzes resumes against job postings and generates targeted questions to improve resume alignment.

## Features

- **POST /session/start**: Analyzes resume and job posting to generate 3 targeted questions
- **POST /session/answer**: Processes answers and returns next question or updated resume
- **GET /session/{session_id}**: Get current session status
- **DELETE /session/{session_id}**: Delete a session
- **GET /health**: Health check endpoint
- **LLM Integration**: Uses OpenRouter API for intelligent question generation and resume updates
- **Session Management**: In-memory session storage with unique session IDs
- **Error Handling**: Comprehensive error handling for invalid sessions and API failures
- **Modular Architecture**: Clean separation of concerns with routers, services, and models

## Architecture

```
BACKEND/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and environment variables
├── models.py              # Pydantic models for request/response validation
├── session_manager.py     # Session storage and management
├── services/
│   └── ai_service.py      # AI/LLM service for API interactions
├── routers/
│   ├── session_router.py  # Session-related endpoints
│   └── health_router.py   # Health and info endpoints
├── requirements.txt       # Python dependencies
├── test_api.py           # Test script
├── run.py                # Enhanced startup script
└── README.md             # This file
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the BACKEND directory:

```env
LLM_API_KEY=your-openrouter-api-key
LLM_MODEL=anthropic/claude-3.5-sonnet
LLM_MAX_TOKENS=2000
LLM_TEMPERATURE=0.7
DEBUG=False
SESSION_TIMEOUT_HOURS=24
```

### 3. Get OpenRouter API Key

1. Sign up at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the dashboard
3. Add it to your `.env` file

### 4. Run the Application

```bash
python run.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

### POST /session/start

Start a new resume analysis session.

**Request Body:**
```json
{
  "resume_text": "\\documentclass{article}\\begin{document}...",
  "job_post": "We are looking for a software engineer..."
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "questions": [
    "Can you provide specific examples of your experience with Python?",
    "What measurable results did you achieve in your most recent role?",
    "Describe a challenging project you led and its outcomes."
  ]
}
```

### POST /session/answer

Submit an answer to the current question.

**Request Body:**
```json
{
  "session_id": "uuid-string",
  "answer": "I led a team of 5 developers to build a microservices architecture..."
}
```

**Response (if more questions):**
```json
{
  "next_question": "What measurable results did you achieve in your most recent role?",
  "updated_resume": null,
  "is_complete": false
}
```

**Response (if all questions answered):**
```json
{
  "next_question": null,
  "updated_resume": "\\documentclass{article}\\begin{document}...",
  "is_complete": true
}
```

### GET /session/{session_id}

Get current session status.

**Response:**
```json
{
  "session_id": "uuid-string",
  "questions": ["Question 1", "Question 2", "Question 3"],
  "answers": ["Answer 1", "Answer 2"],
  "current_question": "Question 3",
  "progress": "2/3",
  "created_at": "2024-01-01T12:00:00"
}
```

### DELETE /session/{session_id}

Delete a session.

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "AI Resume Assistant API",
  "version": "1.0.0"
}
```

## Error Handling

The API includes comprehensive error handling:

- **404 Not Found**: Session not found
- **500 Internal Server Error**: LLM API errors or processing failures
- **422 Unprocessable Entity**: Invalid request data

## LLM Integration

The backend uses OpenRouter API to:

1. **Generate Questions**: Analyze resume and job posting to identify gaps and generate targeted questions
2. **Update Resume**: Use answers to improve resume alignment with job requirements

The AI service includes fallback mechanisms if the API is unavailable.

## Development

### Running in Development Mode

```bash
export DEBUG=True
python run.py
```

### Testing the API

You can test the API using curl or any HTTP client:

```bash
# Start a session
curl -X POST "http://localhost:8000/session/start" \
  -H "Content-Type: application/json" \
  -d '{
    "resume_text": "\\documentclass{article}\\begin{document}Your resume here\\end{document}",
    "job_post": "We are looking for a software engineer with Python experience..."
  }'

# Submit an answer
curl -X POST "http://localhost:8000/session/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "answer": "I have 5 years of Python experience..."
  }'
```

Or use the provided test script:

```bash
python test_api.py
```

## Security Notes

- API keys are loaded from environment variables
- Sessions are stored in memory (consider Redis for production)
- Input validation using Pydantic models
- Error messages don't expose sensitive information

## Production Considerations

1. **Database**: Replace in-memory storage with a database (PostgreSQL, Redis)
2. **Authentication**: Add API key or JWT authentication
3. **Rate Limiting**: Implement rate limiting for API endpoints
4. **Logging**: Add structured logging
5. **Monitoring**: Add health checks and metrics
6. **CORS**: Configure CORS for frontend integration 
# ResumeNhanced

A full-stack AI-powered resume assistant that analyzes LaTeX resumes against job postings, generates targeted questions, and helps you enhance your resume for better job alignment.

---

## Project Structure

```
ResumeNhanced/
├── BACKEND/   # FastAPI backend, DeepSeek LLM, Redis session storage
├── FRONTEND/  # Vite + React + TypeScript frontend
├── README.md  # This file
├── .gitignore # Monorepo .gitignore
```

---

## Features

- **AI Resume Analysis:** Uses DeepSeek LLM to analyze resumes and job postings
- **Targeted Q&A:** Generates and manages targeted questions to improve resumes
- **LaTeX Resume Enhancement:** Updates LaTeX resumes based on user answers
- **Session Management:** Uses Redis for scalable, ephemeral session storage
- **Modern Frontend:** Vite + React + TypeScript UI for editing and AI chat
- **API Integration:** Secure CORS, typed API utilities, and robust error handling

---

## Backend (BACKEND/)

- **Tech:** FastAPI, DeepSeek (via OpenAI client), Redis, Pydantic
- **Key Files:**
  - `main.py` — FastAPI app entry
  - `services/ai_service.py` — LLM integration
  - `session_manager.py` — Redis session storage
  - `routers/` — API endpoints
  - `config.py` — Environment/config management
- **Setup:**
  1. `cd BACKEND`
  2. `python3 -m venv venv && source venv/bin/activate`
  3. `pip install -r requirements.txt`
  4. Create `.env` with:
     ```
     LLM_API_KEY=your-deepseek-api-key
     LLM_API_URL=https://api.deepseek.com
     LLM_MODEL=deepseek-chat
     LLM_MAX_TOKENS=2000
     LLM_TEMPERATURE=0.7
     REDIS_HOST=localhost
     REDIS_PORT=6379
     ```
  5. Start Redis (`redis-server` or Docker)
  6. Run backend: `python run.py` or `uvicorn main:app --reload`

---

## Frontend (FRONTEND/)

- **Tech:** Vite, React, TypeScript, Tailwind CSS
- **Key Files:**
  - `src/pages/Index.tsx` — Main page
  - `src/components/AIChat.tsx` — AI chat and Q&A
  - `src/lib/api.ts` — Typed API utilities
- **Setup:**
  1. `cd FRONTEND`
  2. `npm install`
  3. `npm run dev`
  4. Visit [http://localhost:5173](http://localhost:5173)

---

## Development

- **Backend:**
  - Edit Python files in `BACKEND/`
  - Use `.env` for secrets/config
  - Test LLM with `test_deep_seek.py`
- **Frontend:**
  - Edit React/TS files in `FRONTEND/src/`
  - Use `src/lib/api.ts` for backend calls

---

## Deployment

- **Backend:** Deploy FastAPI app and Redis (Docker Compose recommended)
- **Frontend:** Deploy static build (Vercel, Netlify, etc.)
- **CORS:** Restrict allowed origins in production

---

## API Endpoints (Backend)

- `POST /session/start` — Start a new session
- `POST /session/answer` — Submit an answer
- `GET /session/{session_id}` — Get session status
- `DELETE /session/{session_id}` — Delete a session
- `GET /health` — Health check

---

## Security & Best Practices

- **Secrets:** Never commit `.env` or API keys
- **CORS:** Restrict origins in production
- **Session Storage:** Redis is used for scalability and statelessness
- **Error Handling:** Robust error and fallback logic for LLM/API failures

---

## License

MIT License. See LICENSE file for details. 
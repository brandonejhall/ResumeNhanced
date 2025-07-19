// API utility for backend communication

export interface StartSessionResponse {
  session_id: string;
  first_question: string;
  total_questions: number;
}

export interface AnswerQuestionResponse {
  next_question?: string;
  updated_resume?: string;
  is_complete: boolean;
}

export interface SessionStatusResponse {
  session_id: string;
  questions: string[];
  answers: string[];
  current_question?: string;
  progress: string;
  created_at: string;
}

export interface DeleteSessionResponse {
  message: string;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface Suggestion {
  id: string;
  type: string;
  target_section_header: string;
  context_text_before: string;
  context_text_after: string;
  original_latex_snippet?: string;
  suggested_latex_snippet: string;
  description: string;
}

export interface SuggestionListResponse {
  session_id: string;
  suggestions: Suggestion[];
}

export interface ApplySuggestionRequest {
  suggestion_id: string;
  
}

export interface ApplySuggestionResponse {
  updated_resume_latex: string;
  suggestions: Suggestion[];
}

export interface ApplySuggestionsRequest {
  resume_latex: string;
  accepted_suggestions: Suggestion[];
}

const BASE_URL = 'http://localhost:3002';

export async function startSession(resumeText: string, jobPost: string): Promise<StartSessionResponse> {
  const response = await fetch(`${BASE_URL}/session/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, job_post: jobPost }),
  });
  if (!response.ok) throw new Error('Failed to start session');
  return response.json();
}

export async function answerQuestion(sessionId: string, answer: string): Promise<AnswerQuestionResponse> {
  const response = await fetch(`${BASE_URL}/session/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, answer }),
  });
  if (!response.ok) throw new Error('Failed to answer question');
  return response.json();
}

export async function getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
  const response = await fetch(`${BASE_URL}/session/${sessionId}`);
  if (!response.ok) throw new Error('Failed to get session status');
  return response.json();
}

export async function deleteSession(sessionId: string): Promise<DeleteSessionResponse> {
  const response = await fetch(`${BASE_URL}/session/${sessionId}`, {
    method: 'DELETE',
  });
  if (!response.ok) throw new Error('Failed to delete session');
  return response.json();
}

export async function healthCheck(): Promise<HealthResponse> {
  const response = await fetch(`${BASE_URL}/health`);
  if (!response.ok) throw new Error('Health check failed');
  return response.json();
}

export async function exportPdf(latexContent: string): Promise<Response> {
  return fetch(`${BASE_URL}/export/pdf`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ latex_code: latexContent }),
  });
}

export async function getSuggestions(resumeText: string, jobPost: string): Promise<SuggestionListResponse> {
  const response = await fetch(`${BASE_URL}/session/suggestions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ resume_text: resumeText, job_post: jobPost }),
  });
  if (!response.ok) throw new Error('Failed to get suggestions');
  return response.json();
}

export async function applySuggestion(sessionId: string, req: ApplySuggestionRequest): Promise<ApplySuggestionResponse> {
  const response = await fetch(`${BASE_URL}/session/apply_suggestion/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error('Failed to apply suggestion');
  return response.json();
}

export async function applySuggestions(sessionId: string, req: ApplySuggestionsRequest): Promise<ApplySuggestionResponse> {
  const response = await fetch(`${BASE_URL}/session/apply_suggestions/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!response.ok) throw new Error('Failed to apply suggestions');
  return response.json();
}

export async function getSuggestionsForSession(sessionId: string): Promise<SuggestionListResponse> {
  const response = await fetch(`${BASE_URL}/session/suggestions/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Failed to get suggestions for session');
  }
  return response.json();
} 
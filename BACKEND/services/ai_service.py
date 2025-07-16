"""
AI service for LLM interactions
"""

import openai
import json
from typing import List, Optional
from fastapi import HTTPException
from config import settings
import logging
import re

class AIService:
    """Service for AI/LLM interactions"""
    
    def __init__(self):
        self.api_key = settings.LLM_API_KEY
        self.base_url = settings.LLM_API_URL  # Should be 'https://api.deepseek.com'
        self.model = settings.LLM_MODEL
        self.max_tokens = settings.LLM_MAX_TOKENS
        self.temperature = settings.LLM_TEMPERATURE
        self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.logger = logging.getLogger("AIService")
        logging.basicConfig(level=logging.INFO)

    async def _make_api_call(self, prompt: str, system_message: str = None) -> str:
        """Make API call to DeepSeek via OpenAI client"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        self.logger.info(f"Calling DeepSeek API with model={self.model}, messages={messages}, max_tokens={self.max_tokens}, temperature={self.temperature}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                stream=False
            )
            self.logger.info(f"DeepSeek API response: {response}")
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"DeepSeek API error: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"DeepSeek API error: {str(e)}")
    
    async def analyze_resume_and_job(self, resume_text: str, job_post: str) -> List[str]:
        """Analyze resume and job posting to generate targeted questions"""
        system_message = """You are an expert resume consultant. Analyze resumes and job postings to identify gaps and generate targeted questions that will help improve the resume's alignment with the job requirements."""
        
        prompt = f"""
        Analyze this resume and job posting to identify gaps and generate exactly 3 targeted questions.
        
        RESUME:
        {resume_text}
        
        JOB POSTING:
        {job_post}
        
        Generate exactly 3 specific questions that will help fill gaps between the resume and job requirements.
        Focus on:
        1. Missing skills or experiences that are mentioned in the job posting
        2. Quantifiable achievements and metrics
        3. Specific projects or accomplishments that demonstrate relevant experience
        
        Return ONLY a JSON array of exactly 3 questions as strings. Example format:
        ["Question 1?", "Question 2?", "Question 3?"]
        """
        
        try:
            response = await self._make_api_call(prompt, system_message)
            # Remove markdown code block fencing if present
            cleaned = re.sub(r'^```json\s*|```$', '', response.strip(), flags=re.MULTILINE).strip()
            questions = json.loads(cleaned)
            
            if not isinstance(questions, list) or len(questions) != 3:
                raise ValueError("Invalid response format")
            
            return questions
        except Exception as e:
            # Fallback questions if LLM call fails
            return self._get_fallback_questions()
    
    async def enhance_resume(self, resume_text: str, job_post: str, questions: List[str], answers: List[str]) -> str:
        """Enhance resume based on answers provided"""
        system_message = """You are an expert resume writer. Update LaTeX resumes to better align with job requirements while maintaining proper LaTeX formatting."""
        
        qa_pairs = '\n'.join(
            f"Q{i+1}: {q}\nA{i+1}: {a}"
            for i, (q, a) in enumerate(zip(questions, answers))
        )
        
        prompt = f"""
        Update this LaTeX resume based on the answers provided to make it more relevant to the job posting.
        
        ORIGINAL RESUME:
        {resume_text}
        
        JOB POSTING:
        {job_post}
        
        QUESTIONS AND ANSWERS:
        {qa_pairs}
        
        Update the resume by:
        1. Adding relevant information from the answers to appropriate sections
        2. Strengthening sections that align with job requirements
        3. Maintaining proper LaTeX formatting and structure
        4. Keeping the content professional and concise
        5. Ensuring the resume flows logically
        
        Return ONLY the updated LaTeX resume text.
        """
        
        try:
            updated_resume = await self._make_api_call(prompt, system_message)
            return updated_resume
        except Exception as e:
            # Return original resume if LLM call fails
            return resume_text
    
    def _get_fallback_questions(self) -> List[str]:
        """Get fallback questions when LLM is unavailable"""
        return [
            "Can you provide specific examples of your experience with the key skills mentioned in the job posting?",
            "What measurable results or metrics did you achieve in your most recent role?",
            "Describe a challenging project you led that demonstrates your ability to handle the responsibilities mentioned in this role."
        ]

# Global AI service instance
ai_service = AIService() 
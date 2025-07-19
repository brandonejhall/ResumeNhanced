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
import uuid
from models import Suggestion

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
        system_message = """You are an expert resume writer. Suggest LaTeX snippet(s) or section(s) to add or change in the resume to better align with the job requirements, while maintaining proper LaTeX formatting. Do NOT return the entire resume, only the relevant snippet(s) or section(s) to be inserted or replaced. Clearly indicate where each change should be applied (e.g., section name or line number). Wrap each suggested snippet with '% === AI SUGGESTION START ===' and '% === AI SUGGESTION END ===' comments."""
        
        qa_pairs = '\n'.join(
            f"Q{i+1}: {q}\nA{i+1}: {a}"
            for i, (q, a) in enumerate(zip(questions, answers))
        )
        
        prompt = f"""
        Based on the answers provided, suggest only the LaTeX snippet(s) or section(s) that should be added or changed in the resume to make it more relevant to the job posting.
        
        ORIGINAL RESUME:
        {resume_text}
        
        JOB POSTING:
        {job_post}
        
        QUESTIONS AND ANSWERS:
        {qa_pairs}
        
        Instructions:
        - Do NOT return the entire resume.
        - Only return the LaTeX snippet(s) or section(s) to be inserted or replaced.
        - Clearly indicate where each change should be applied (e.g., section name or line number).
        - Maintain proper LaTeX formatting and structure.
        - Keep the content professional and concise.
        - Ensure the resume flows logically.
        - Wrap each suggested snippet with '% === AI SUGGESTION START ===' and '% === AI SUGGESTION END ===' comments.
        
        Return ONLY the LaTeX snippet(s) or section(s) to be added or changed.
        """
        
        try:
            updated_snippet = await self._make_api_call(prompt, system_message)
            return updated_snippet
        except Exception as e:
            # Return empty string if LLM call fails
            return ""
    
    def _get_fallback_questions(self) -> List[str]:
        """Get fallback questions when LLM is unavailable"""
        return [
            "Can you provide specific examples of your experience with the key skills mentioned in the job posting?",
            "What measurable results or metrics did you achieve in your most recent role?",
            "Describe a challenging project you led that demonstrates your ability to handle the responsibilities mentioned in this role."
        ]

    def build_suggestion_prompt(self, parsed_resume, job_post, questions=None, answers=None):
        """Build a prompt for the LLM to return structured suggestions as JSON objects."""
        qa_context = ""
        if questions and answers:
            qa_pairs = '\n'.join(f"Q{i+1}: {q}\nA{i+1}: {a}" for i, (q, a) in enumerate(zip(questions, answers)))
            qa_context = f"\n\nQUESTIONS AND ANSWERS:\n{qa_pairs}"
        
        # Convert parsed resume to readable format
        resume_structure = ""
        for section in parsed_resume:
            resume_structure += f"\nSection: {section['section']}\n"
            for sub in section['subheadings']:
                if sub['type'] == 'subheading':
                    resume_structure += f"  - {sub['title']} at {sub['location']} ({sub['role']}, {sub['dates']})\n"
                elif sub['type'] == 'item':
                    resume_structure += f"    * {sub['content']}\n"
        
        return f"""
        Given the following LaTeX resume structure and job posting, generate a list of suggestions as JSON objects.
        
        RESUME STRUCTURE:
        {resume_structure}
        
        JOB POSTING:
        {job_post}
        {qa_context}
        
        IMPORTANT: Generate suggestions based ONLY on the information provided in the Q&A context. Do not fabricate or assume any experience that wasn't explicitly mentioned by the user. Focus on enhancing existing information or adding sections that can be truthfully filled based on the user's actual experience.
        
        Each suggestion must be a JSON object with the following fields:
        - id: a unique identifier (UUID)
        - type: one of 'replace_section', 'add_item_to_section', 'update_item_in_section', 'add_new_section'
        - target_section_header: the section header (e.g., 'Experience')
        - context_text_before: a snippet of LaTeX before the change
        - context_text_after: a snippet of LaTeX after the change
        - original_latex_snippet: the original LaTeX to be replaced (if applicable)
        - suggested_latex_snippet: the new LaTeX to insert or replace
        - description: a human-readable explanation of the change
        
        Return ONLY a JSON array of these suggestion objects.
        """

    async def generate_structured_suggestions(self, parsed_resume, job_post, questions=None, answers=None):
        """Generate structured suggestions using the LLM and return a list of Suggestion objects."""
        import json
        import uuid
        from models import Suggestion
        system_message = "You are an expert resume consultant. Given a parsed LaTeX resume and a job posting, generate a list of fine-grained, actionable suggestions to improve the resume. Each suggestion must be a JSON object with the following fields: id (UUID), type (replace_section, add_item_to_section, update_item_in_section, add_new_section), target_section_header, context_text_before, context_text_after, original_latex_snippet, suggested_latex_snippet, description. IMPORTANT: Only suggest changes based on information that was explicitly provided by the user. Do not fabricate experience or skills. Return ONLY a JSON array of these objects."
        prompt = self.build_suggestion_prompt(parsed_resume, job_post, questions, answers)
        try:
            response = await self._make_api_call(prompt, system_message)
            self.logger.info(f"Raw LLM response: {response}")
            
            if not response or not response.strip():
                self.logger.error("Empty response from LLM")
                return []
            
            cleaned = re.sub(r'^```json\s*|```$', '', response.strip(), flags=re.MULTILINE).strip()
            self.logger.info(f"Cleaned response: {cleaned}")
            
            if not cleaned:
                self.logger.error("Empty response after cleaning")
                return []
            
            suggestions_data = json.loads(cleaned)
            self.logger.info(f"Parsed suggestions data: {suggestions_data}")
            
            suggestions = []
            for s in suggestions_data:
                # Ensure UUID
                if not s.get('id'):
                    s['id'] = str(uuid.uuid4())
                suggestions.append(Suggestion(**s))
            return suggestions
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            self.logger.error(f"Response that failed to parse: {response if 'response' in locals() else 'No response'}")
            return []
        except Exception as e:
            self.logger.error(f"Failed to generate structured suggestions: {e}")
            return []

    def parse_resume_latex(self, latex_string):
        """Parse the LaTeX resume into a structured representation for known template."""
        # Parse \section{...}
        import re
        sections = []
        section_pattern = re.compile(r'\\section\{([^}]*)\}')
        subheading_pattern = re.compile(r'\\resumeSubheading\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}\s*\{([^}]*)\}')
        item_pattern = re.compile(r'\\resumeItem\{([^}]*)\}')
        lines = latex_string.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i]
            section_match = section_pattern.search(line)
            if section_match:
                section_name = section_match.group(1)
                section_start = i
                section_content = []
                i += 1
                # Collect lines until next section or end
                while i < len(lines) and not section_pattern.search(lines[i]):
                    section_content.append(lines[i])
                    i += 1
                section_end = i - 1
                # Parse subheadings and items within section
                subheadings = []
                for j, subline in enumerate(section_content):
                    subheading_match = subheading_pattern.search(subline)
                    if subheading_match:
                        subheadings.append({
                            'type': 'subheading',
                            'title': subheading_match.group(1),
                            'location': subheading_match.group(2),
                            'role': subheading_match.group(3),
                            'dates': subheading_match.group(4),
                            'line': section_start + j + 1
                        })
                    item_match = item_pattern.search(subline)
                    if item_match:
                        subheadings.append({
                            'type': 'item',
                            'content': item_match.group(1),
                            'line': section_start + j + 1
                        })
                sections.append({
                    'section': section_name,
                    'start_line': section_start + 1,
                    'end_line': section_end + 1,
                    'subheadings': subheadings
                })
            else:
                i += 1
        return sections

    def apply_suggestion(self, parsed_resume, suggestion: Suggestion):
        """Apply a suggestion to the parsed resume structure."""
        import difflib
        # Find the target section
        for section in parsed_resume:
            if section['section'] == suggestion.target_section_header:
                # Find context in section lines
                section_lines = section['end_line'] - section['start_line'] + 1
                # Try to find context_text_before and context_text_after
                before_idx = None
                after_idx = None
                for sub in section['subheadings']:
                    if suggestion.context_text_before and suggestion.context_text_before.strip() in sub.get('content', ''):
                        before_idx = sub['line']
                    if suggestion.context_text_after and suggestion.context_text_after.strip() in sub.get('content', ''):
                        after_idx = sub['line']
                # Fallback: fuzzy match
                if before_idx is None and suggestion.context_text_before:
                    for sub in section['subheadings']:
                        if difflib.SequenceMatcher(None, suggestion.context_text_before.strip(), sub.get('content', '')).ratio() > 0.7:
                            before_idx = sub['line']
                if after_idx is None and suggestion.context_text_after:
                    for sub in section['subheadings']:
                        if difflib.SequenceMatcher(None, suggestion.context_text_after.strip(), sub.get('content', '')).ratio() > 0.7:
                            after_idx = sub['line']
                # Apply suggestion based on type
                if suggestion.type == 'add_item_to_section':
                    # Insert after before_idx or at end
                    insert_line = before_idx if before_idx else section['end_line']
                    section['subheadings'].append({
                        'type': 'item',
                        'content': suggestion.suggested_latex_snippet,
                        'line': insert_line + 1
                    })
                elif suggestion.type == 'replace_section':
                    # Replace all lines in section
                    section['subheadings'] = [{
                        'type': 'raw',
                        'content': suggestion.suggested_latex_snippet,
                        'line': section['start_line']
                    }]
                elif suggestion.type == 'update_item_in_section':
                    # Find and replace the item
                    for sub in section['subheadings']:
                        if suggestion.original_latex_snippet.strip() == sub.get('content', '').strip():
                            sub['content'] = suggestion.suggested_latex_snippet
                elif suggestion.type == 'add_new_section':
                    # Add a new section at the end
                    parsed_resume.append({
                        'section': suggestion.target_section_header,
                        'start_line': 0,
                        'end_line': 0,
                        'subheadings': [{
                            'type': 'raw',
                            'content': suggestion.suggested_latex_snippet,
                            'line': 0
                        }]
                    })
        return parsed_resume

    def serialize_resume_latex(self, parsed_resume):
        """Convert the parsed resume structure back to a LaTeX string."""
        lines = []
        for section in parsed_resume:
            lines.append(f"\\section{{{section['section']}}}")
            for sub in section['subheadings']:
                if sub['type'] == 'subheading':
                    lines.append(f"\\resumeSubheading{{{sub['title']}}}{{{sub['location']}}}{{{sub['role']}}}{{{sub['dates']}}}")
                elif sub['type'] == 'item':
                    lines.append(f"\\resumeItem{{{sub['content']}}}")
                elif sub['type'] == 'raw':
                    lines.append(sub['content'])
        return '\n'.join(lines)

# Global AI service instance
ai_service = AIService() 
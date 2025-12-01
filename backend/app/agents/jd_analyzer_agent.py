"""JD Analyzer Agent - Analyzes job descriptions for keywords and requirements."""
import json
import os
import asyncio
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from ..models.job_description import JobDescription


class JDAnalysis(Dict[str, Any]):
    """Analysis results from job description."""
    pass


class JDAnalyzerAgent:
    """Agent that analyzes job descriptions to extract requirements and keywords."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize the JD analyzer agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        self.agent = Agent(
            name="jd_analyzer_agent",
            model=LiteLlm(model="gpt-4o-mini"),
            instruction="""You are an expert HR analyst specializing in job descriptions.

Analyze the given job description and extract:

1. **Must-have technical skills**: Technologies, languages, frameworks explicitly required
2. **Nice-to-have skills**: Preferred or bonus skills mentioned
3. **Key responsibilities**: Main duties and tasks
4. **Important keywords**: Industry terms, buzzwords, action verbs frequently used
5. **Experience requirements**: Years of experience, seniority level
6. **Domain knowledge**: Industry-specific knowledge required
7. **Soft skills**: Communication, leadership, teamwork, etc.

Return ONLY valid JSON:
{
    "must_have_skills": ["Python", "FastAPI", "PostgreSQL"],
    "nice_to_have_skills": ["Docker", "Kubernetes"],
    "key_responsibilities": ["Design scalable APIs", "Mentor junior developers"],
    "important_keywords": ["scalable", "microservices", "agile", "CI/CD"],
    "experience_level": "Senior (5+ years)",
    "domain_knowledge": ["Healthcare", "HIPAA compliance"],
    "soft_skills": ["leadership", "communication", "problem-solving"],
    "ats_keywords": ["API", "RESTful", "database design", "cloud"],
    "seniority": "senior",
    "company_culture": ["collaborative", "fast-paced"]
}

Focus on extracting actual ATS keywords that will be scanned. Be thorough.""",
            description="Analyzes job descriptions to identify key requirements and keywords.",
            output_key="jd_analysis"
        )
    
    async def analyze(self, job_description: JobDescription) -> JDAnalysis:
        """Analyze a job description to extract requirements and keywords.
        
        Args:
            job_description: The job description to analyze.
            
        Returns:
            JDAnalysis: Dictionary containing extracted requirements and keywords.
            
        Raises:
            ValueError: If analysis fails or JSON is invalid.
        """
        # Prepare JD text
        jd_text = f"""
Title: {job_description.title}
Company: {job_description.company}
Location: {getattr(job_description, 'location', 'Not specified') or 'Not specified'}
Salary: {getattr(job_description, 'salary_range', 'Not specified') or 'Not specified'}

Description:
{job_description.description}

Requirements:
{chr(10).join(job_description.requirements) if job_description.requirements else 'See description'}

Responsibilities:
{chr(10).join(job_description.responsibilities) if job_description.responsibilities else 'See description'}

Preferred Qualifications:
{chr(10).join(getattr(job_description, 'preferred_qualifications', [])) if getattr(job_description, 'preferred_qualifications', []) else 'None specified'}
"""
        
        # Create runner and execute agent
        runner = InMemoryRunner(agent=self.agent)
        
        # Run the agent asynchronously
        prompt = f"Job Description:\n{jd_text}\n\nExtract all requirements and keywords and return ONLY the JSON."
        result = await runner.run_debug(prompt)
        
        # Extract analysis JSON from the response events
        analysis_json_str = ""
        if isinstance(result, list):
            for event in result:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            analysis_json_str = part.text
                            break
                if analysis_json_str:
                    break
        
        # Remove markdown code blocks if present
        analysis_json_str = analysis_json_str.strip()
        if analysis_json_str.startswith('```'):
            lines = analysis_json_str.split('\n')
            analysis_json_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else analysis_json_str
            if analysis_json_str.startswith('json'):
                analysis_json_str = analysis_json_str[4:].strip()
        
        try:
            analysis = json.loads(analysis_json_str)
            return JDAnalysis(analysis)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JD analysis JSON: {e}\nOutput: {analysis_json_str}")

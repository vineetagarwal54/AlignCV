"""Parser Agent - Extracts structured Resume from raw text using OpenAI."""
import json
import os
import asyncio
from typing import Dict, Any
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from ..models.resume import Resume, Experience, Education, Project, Certification


class ParserAgent:
    """Agent that parses raw resume text into structured Resume object."""
    
    def __init__(self, api_key: str = None):
        """Initialize the parser agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        # Create the parsing agent with OpenAI GPT-4o-mini
        self.agent = Agent(
            name="parser_agent",
            model=LiteLlm(model="gpt-4o-mini"),
            instruction="""You are an expert resume parser. Your task is to extract structured information from resume text.

Given raw resume text, extract:
- Full name, email, phone, location, LinkedIn, GitHub, portfolio
- Professional summary
- Technical skills (as list)
- Work experiences (company, position, dates, location, bullet points)
- Education (institution, degree, field, dates, GPA, courses)
- Projects (name, dates, technologies, description, bullet points)
- Certifications (name, issuer, date, credential ID/URL)

Return ONLY valid JSON matching this structure:
{
    "full_name": "string",
    "email": "string (optional)",
    "phone": "string (optional)",
    "location": "string (optional)",
    "linkedin": "string (optional)",
    "github": "string (optional)",
    "website": "string (optional)",
    "summary": "string (optional)",
    "technical_skills": ["skill1", "skill2"],
    "experiences": [
        {
            "company": "string",
            "title": "string",
            "start_date": "string (e.g., '2020-01')",
            "end_date": "string or 'Present'",
            "location": "string (optional)",
            "bullet_points": ["achievement 1", "achievement 2"]
        }
    ],
    "education": [
        {
            "institution": "string",
            "degree": "string",
            "field_of_study": "string (optional)",
            "graduation_date": "string (optional)",
            "gpa": "string (optional)",
            "honors": ["honor1"] (optional)
        }
    ],
    "projects": [
        {
            "name": "string",
            "description": "string",
            "technologies": ["tech1"],
            "url": "string (optional)",
            "bullet_points": ["detail1"]
        }
    ],
    "certifications": [
        {
            "name": "string",
            "issuer": "string",
            "date_obtained": "string (optional)",
            "credential_id": "string (optional)",
            "expiry_date": "string (optional)"
        }
    ]
}

Be accurate. Extract dates in YYYY-MM format when possible. Preserve all achievements verbatim.
Do NOT add fields or information not present in the resume text.""",
            description="Parses raw resume text into structured JSON format.",
            output_key="parsed_resume"
        )
    
    async def parse(self, resume_text: str) -> Resume:
        """Parse raw resume text into a Resume object.
        
        Args:
            resume_text: Raw text extracted from resume document.
            
        Returns:
            Resume: Structured resume object.
            
        Raises:
            ValueError: If parsing fails or JSON is invalid.
        """
        # Create runner and execute agent
        runner = InMemoryRunner(agent=self.agent)
        
        # Run the agent asynchronously
        prompt = f"Resume text:\n{resume_text}\n\nExtract all information and return ONLY the JSON."
        result = await runner.run_debug(prompt)
        
        # Extract parsed JSON from the response events
        parsed_json_str = ""
        if isinstance(result, list):
            for event in result:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            parsed_json_str = part.text
                            break
                if parsed_json_str:
                    break
        
        # Remove markdown code blocks if present
        parsed_json_str = parsed_json_str.strip()
        if parsed_json_str.startswith('```'):
            lines = parsed_json_str.split('\n')
            parsed_json_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else parsed_json_str
            if parsed_json_str.startswith('json'):
                parsed_json_str = parsed_json_str[4:].strip()
        
        # Parse JSON string
        try:
            parsed_data = json.loads(parsed_json_str)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse resume JSON: {e}\nOutput: {parsed_json_str}")
        
        # Convert to Resume object
        try:
            # Convert nested structures
            if "experiences" in parsed_data:
                parsed_data["experiences"] = [
                    Experience(**exp) for exp in parsed_data["experiences"]
                ]
            
            if "education" in parsed_data:
                parsed_data["education"] = [
                    Education(**edu) for edu in parsed_data["education"]
                ]
            
            if "projects" in parsed_data:
                parsed_data["projects"] = [
                    Project(**proj) for proj in parsed_data["projects"]
                ]
            
            if "certifications" in parsed_data:
                parsed_data["certifications"] = [
                    Certification(**cert) for cert in parsed_data["certifications"]
                ]
            
            resume = Resume(**parsed_data)
            return resume
            
        except Exception as e:
            raise ValueError(f"Failed to create Resume object: {e}\nParsed data: {parsed_data}")

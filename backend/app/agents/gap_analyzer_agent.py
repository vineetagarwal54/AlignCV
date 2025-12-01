"""Gap Analyzer Agent - Identifies gaps between resume and JD requirements."""
import json
import os
import asyncio
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from ..models.resume import Resume
from ..models.job_description import JobDescription


class GapAnalysis(Dict[str, Any]):
    """Gap analysis results."""
    pass


class GapAnalyzerAgent:
    """Agent that identifies gaps between resume and job requirements."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize the gap analyzer agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        self.agent = Agent(
            name="gap_analyzer_agent",
            model=LiteLlm(model="gpt-4o-mini"),
            instruction="""You are an expert resume consultant analyzing skill gaps.

Given:
- A resume (candidate's current profile)
- A job description analysis (required skills, keywords, responsibilities)

Identify:
1. **Missing must-have skills**: Required skills not mentioned in resume
2. **Missing keywords**: Important ATS keywords absent from resume
3. **Underemphasized strengths**: Skills candidate has but didn't highlight enough
4. **Experience gaps**: Areas where candidate lacks sufficient detail or examples
5. **Sections to enhance**: Which resume sections need improvement
6. **Potential matches**: Existing experience that could be reframed to match JD

Return ONLY valid JSON:
{{
    "missing_must_have_skills": ["Kubernetes", "GraphQL"],
    "missing_keywords": ["scalable", "microservices", "agile"],
    "underemphasized_strengths": ["Python (mentioned only once)", "Leadership"],
    "experience_gaps": [
        {{
            "gap": "No cloud infrastructure experience shown",
            "suggestion": "Reframe project X to highlight AWS usage"
        }}
    ],
    "sections_to_enhance": [
        {{
            "section": "experiences[0]",
            "reason": "Missing key responsibilities mentioned in JD",
            "priority": "high"
        }}
    ],
    "potential_matches": [
        {{
            "resume_item": "Built REST APIs using Python",
            "jd_requirement": "Design scalable microservices",
            "alignment_strategy": "Emphasize scalability and architecture"
        }}
    ],
    "overall_match_percentage": 65,
    "priority_improvements": ["Add Kubernetes experience", "Highlight scalability"]
}}

Be specific and actionable. Focus on truthful enhancements, not fabrication.""",
            description="Identifies gaps between resume and job requirements.",
            output_key="gap_analysis"
        )
    
    async def analyze_gaps(
        self, 
        resume: Resume, 
        job_description: JobDescription,
        jd_analysis: Dict[str, Any]
    ) -> GapAnalysis:
        """Analyze gaps between resume and job requirements.
        
        Args:
            resume: The candidate's resume.
            job_description: The target job description.
            jd_analysis: Analysis of the JD from JDAnalyzerAgent.
            
        Returns:
            GapAnalysis: Dictionary containing identified gaps and improvement suggestions.
            
        Raises:
            ValueError: If analysis fails or JSON is invalid.
        """
        # Prepare resume summary (build as string to avoid template variable issues)
        name_line = f"Name: {resume.full_name}"
        summary_line = f"Summary: {resume.summary or 'None'}"
        skills_line = f"Skills: {', '.join(resume.technical_skills) if resume.technical_skills else 'None'}"
        exp_section = f"Experiences:\n{self._format_experiences(resume)}"
        edu_section = f"Education:\n{self._format_education(resume)}"
        proj_section = f"Projects:\n{self._format_projects(resume)}"
        
        resume_summary = f"{name_line}\n{summary_line}\n{skills_line}\n\n{exp_section}\n\n{edu_section}\n\n{proj_section}"
        
        # Run the agent
        prompt = f"""Resume Summary:
{resume_summary}

Job Description:
Title: {job_description.title}
Company: {job_description.company}
{job_description.description}

JD Analysis:
{json.dumps(jd_analysis, indent=2)}

Analyze gaps and return JSON."""
        
        runner = InMemoryRunner(agent=self.agent)
        result_events = await runner.run_debug(prompt)
        
        # Extract analysis from response events
        gap_str = ""
        if isinstance(result_events, list):
            for event in result_events:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            gap_str = part.text
                            break
                if gap_str:
                    break
        
        # Remove markdown code blocks if present
        gap_str = gap_str.strip()
        if gap_str.startswith('```'):
            lines = gap_str.split('\n')
            gap_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else gap_str
            if gap_str.startswith('json'):
                gap_str = gap_str[4:].strip()
        
        try:
            gap_analysis = json.loads(gap_str)
            return GapAnalysis(gap_analysis)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse gap analysis JSON: {e}\nOutput: {gap_str}")
    
    def _format_experiences(self, resume: Resume) -> str:
        """Format experiences for display."""
        if not resume.experiences:
            return "None"
        
        lines = []
        for i, exp in enumerate(resume.experiences):
            lines.append(f"{i+1}. {exp.title} at {exp.company} ({exp.start_date} - {exp.end_date})")
            if exp.bullet_points:
                for bullet in exp.bullet_points:
                    lines.append(f"   - {bullet}")
        return "\n".join(lines)
    
    def _format_education(self, resume: Resume) -> str:
        """Format education for display."""
        if not resume.education:
            return "None"
        
        lines = []
        for edu in resume.education:
            lines.append(f"- {edu.degree} in {edu.field_of_study or 'N/A'} from {edu.institution}")
        return "\n".join(lines)
    
    def _format_projects(self, resume: Resume) -> str:
        """Format projects for display."""
        if not resume.projects:
            return "None"
        
        lines = []
        for proj in resume.projects:
            tech = ', '.join(proj.technologies) if proj.technologies else 'N/A'
            lines.append(f"- {proj.name} (Tech: {tech})")
        return "\n".join(lines)

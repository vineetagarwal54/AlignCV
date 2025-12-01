"""Rewrite Agent - Rewrites resume content to align with JD while preserving truth."""
import json
import os
import asyncio
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import InMemoryRunner
from ..models.resume import Resume
from ..models.alignment import DiffObject, ChangeType


class RewriteResult(Dict[str, Any]):
    """Result from rewrite operation."""
    pass


class RewriteAgent:
    """Agent that rewrites resume bullets and sections to align with JD."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize the rewrite agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        self.agent = Agent(
            name="rewrite_agent",
            model=LiteLlm(model="gpt-4o-mini"),
            instruction="""You are an expert resume writer specializing in ATS optimization.

Given:
- Original resume content
- Gap analysis showing missing keywords and underemphasized strengths
- Job description requirements

Your task: Rewrite resume content to maximize ATS score while maintaining truthfulness.

IMPORTANT: Return the COMPLETE updated resume with ALL fields (full_name, email, summary, experiences, education, projects, etc), not just the changed fields.

RULES:
1. **Never fabricate**: Only enhance/rephrase existing accomplishments
2. **Add JD keywords**: Naturally integrate missing keywords where relevant
3. **Use action verbs**: Start bullets with strong verbs (Led, Architected, Optimized, etc.)
4. **Quantify when possible**: Add metrics if implicitly present
5. **Match tone**: Use language/terms from the job description
6. **Keep structure**: Preserve the original resume format
7. **Emphasize impact**: Highlight results and outcomes

Return ONLY valid JSON:
{{
    "updated_resume": {{
        "summary": "updated summary text",
        "technical_skills": ["skill1", "skill2"],
        "experiences": [
            {{
                "company": "...",
                "title": "...",
                "start_date": "...",
                "end_date": "...",
                "location": "...",
                "bullet_points": ["rewritten bullet 1", "rewritten bullet 2"]
            }}
        ],
        "education": [...],
        "projects": [...]
    }},
    "changes": [
        {{
            "section": "experiences[0].bullet_points[0]",
            "field": "text",
            "change_type": "modified",
            "original_value": "Built APIs",
            "new_value": "Architected scalable RESTful APIs using Python and FastAPI",
            "reason": "Added keywords: scalable, RESTful, FastAPI from JD",
            "confidence_score": 0.95
        }}
    ]
}}

Rewrite strategically to maximize ATS match.""",
            description="Rewrites resume content to align with job requirements.",
            output_key="current_draft"
        )
    
    async def rewrite(
        self,
        resume: Resume,
        gap_analysis: Dict[str, Any],
        jd_analysis: Dict[str, Any]
    ) -> RewriteResult:
        """Rewrite resume to align with job requirements.
        
        Args:
            resume: Original resume to rewrite.
            gap_analysis: Gap analysis from GapAnalyzerAgent.
            jd_analysis: JD analysis from JDAnalyzerAgent.
            
        Returns:
            RewriteResult: Dictionary containing updated resume and list of changes.
            
        Raises:
            ValueError: If rewrite fails or JSON is invalid.
        """
        # Convert resume to dict for context (mode='json' handles datetime serialization)
        resume_dict = resume.model_dump(mode='json', exclude_none=True)
        
        # Extract target keywords
        target_keywords = []
        target_keywords.extend(jd_analysis.get("must_have_skills", []))
        target_keywords.extend(jd_analysis.get("important_keywords", []))
        target_keywords.extend(jd_analysis.get("ats_keywords", []))
        
        # Run the agent
        prompt = f"""Original Resume:
{json.dumps(resume_dict, indent=2)}

Gap Analysis:
{json.dumps(gap_analysis, indent=2)}

Target Keywords:
{json.dumps(target_keywords[:20], indent=2)}

Rewrite the resume and return JSON."""
        
        runner = InMemoryRunner(agent=self.agent)
        result_events = await runner.run_debug(prompt)
        
        # Extract rewrite result from response events
        rewrite_str = ""
        if isinstance(result_events, list):
            for event in result_events:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            rewrite_str = part.text
                            break
                if rewrite_str:
                    break
        
        # Remove markdown code blocks if present
        rewrite_str = rewrite_str.strip()
        if rewrite_str.startswith('```'):
            lines = rewrite_str.split('\n')
            rewrite_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else rewrite_str
            if rewrite_str.startswith('json'):
                rewrite_str = rewrite_str[4:].strip()
        try:
            rewrite_result = json.loads(rewrite_str)
            return RewriteResult(rewrite_result)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse rewrite result JSON: {e}\nOutput: {rewrite_str}")
            raise ValueError(f"Failed to parse rewrite result JSON: {e}\nOutput: {rewrite_json_str}")

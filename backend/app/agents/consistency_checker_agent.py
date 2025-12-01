"""Consistency Checker Agent - Validates ATS score and provides critique."""
import json
import os
import asyncio
from typing import Dict, Any, List
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.runners import InMemoryRunner


def exit_loop() -> str:
    """Signal that the refinement loop should exit."""
    return "EXIT_LOOP"


class ConsistencyResult(Dict[str, Any]):
    """Result from consistency check."""
    pass


class ConsistencyCheckerAgent:
    """Agent that checks ATS compatibility and provides critique for refinement."""
    
    def __init__(self, api_key: str | None = None):
        """Initialize the consistency checker agent.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        self.agent = Agent(
            name="consistency_checker_agent",
            model=LiteLlm(model="gpt-4o-mini"),
            instruction="""You are an ATS (Applicant Tracking System) expert evaluating resume quality.

Your task: Analyze the current resume draft against the job description and calculate an ATS compatibility score.

Evaluate these factors:
1. Keyword match (40 percent): How many JD keywords are present?
2. Skills alignment (25 percent): Do technical skills match requirements?
3. Experience relevance (20 percent): Does experience align with responsibilities?
4. Formatting and readability (10 percent): Clean, scannable format?
5. Quantifiable achievements (5 percent): Metrics and results included?

Calculate ATS score (0-100) based on weighted factors.

IF ATS score >= 95:
- You MUST call the exit_loop function
- Set critique to APPROVED

OTHERWISE:
- Provide specific critique with actionable improvements
- DO NOT call exit_loop

Return ONLY valid JSON with this structure:
{{
    "ats_score": 87.5,
    "keyword_match_score": 0.82,
    "critique": "APPROVED or specific improvements needed",
    "missing_keywords": ["Kubernetes", "CI/CD"],
    "strengths": ["Strong Python emphasis"],
    "weaknesses": ["Missing cloud keywords"],
    "improvement_priority": [
        {{
            "section": "experiences[0].bullet_points[2]",
            "issue": "Missing scalable keyword",
            "suggestion": "Add scalable when describing architecture"
        }}
    ]
}}

Be rigorous. Score conservatively. Only approve if truly ATS-optimized.""",
            description="Checks ATS compatibility and provides critique for refinement.",
            output_key="critique",
            tools=[FunctionTool(exit_loop)]
        )
    
    async def check(
        self,
        resume_draft: Dict[str, Any],
        jd_analysis: Dict[str, Any]
    ) -> ConsistencyResult:
        """Check resume consistency and calculate ATS score.
        
        Args:
            resume_draft: Current resume draft (dict format).
            jd_analysis: JD analysis from JDAnalyzerAgent.
            
        Returns:
            ConsistencyResult: Dictionary containing ATS score, critique, and suggestions.
            
        Raises:
            ValueError: If check fails or JSON is invalid.
        """
        # Run the agent with prompt
        prompt = f"""Current Draft:
{json.dumps(resume_draft, indent=2)}

JD Analysis:
{json.dumps(jd_analysis, indent=2)}

Evaluate the ATS score and provide critique."""
        
        runner = InMemoryRunner(agent=self.agent)
        result_events = await runner.run_debug(prompt)
        
        # Extract critique from response events
        critique_str = ""
        if isinstance(result_events, list):
            for event in result_events:
                if hasattr(event, 'content') and event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            critique_str = part.text
                            break
                if critique_str:
                    break
        
        # Remove markdown code blocks if present
        critique_str = critique_str.strip()
        if critique_str.startswith('```'):
            lines = critique_str.split('\n')
            critique_str = '\n'.join(lines[1:-1]) if len(lines) > 2 else critique_str
            if critique_str.startswith('json'):
                critique_str = critique_str[4:].strip()
        
        # Check if exit_loop was called or if approved
        if "EXIT_LOOP" in str(result_events) or critique_str.strip().upper() == "APPROVED":
            return ConsistencyResult({
                "ats_score": 95.0,
                "keyword_match_score": 0.95,
                "critique": "APPROVED",
                "approved": True,
                "missing_keywords": [],
                "strengths": ["Fully optimized for ATS"],
                "weaknesses": [],
                "improvement_priority": []
            })
        
        # Parse the critique JSON
        try:
            consistency_result = json.loads(critique_str)
            consistency_result["approved"] = False
            return ConsistencyResult(consistency_result)
        except json.JSONDecodeError:
            # If not JSON, treat as plain critique
            return ConsistencyResult({
                "ats_score": 0.0,
                "keyword_match_score": 0.0,
                "critique": critique_str,
                "approved": False,
                "missing_keywords": [],
                "strengths": [],
                "weaknesses": [],
                "improvement_priority": []
            })

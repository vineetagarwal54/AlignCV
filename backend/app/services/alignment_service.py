"""Alignment Service - Orchestrates multi-agent pipeline for resume alignment."""
import time
import os
from typing import List, Dict, Any, Optional
from ..models.resume import Resume, Experience, Education, Project, Certification
from ..models.job_description import JobDescription
from ..models.alignment import (
    AlignmentRequest, 
    AlignmentResponse, 
    AlignmentMetrics,
    DiffObject,
    ChangeType
)
from ..agents.parser_agent import ParserAgent
from ..agents.jd_analyzer_agent import JDAnalyzerAgent
from ..agents.gap_analyzer_agent import GapAnalyzerAgent
from ..agents.rewrite_agent import RewriteAgent
from ..agents.consistency_checker_agent import ConsistencyCheckerAgent
from ..services.latex_renderer import LaTeXRenderer


class AlignmentService:
    """Orchestrates the multi-agent alignment pipeline."""
    
    def __init__(self, api_key: str | None = None, max_iterations: int = 3):
        """Initialize the alignment service.
        
        Args:
            api_key: OpenAI API key. If None, reads from OPENAI_API_KEY env var.
            max_iterations: Maximum refinement iterations (default: 3).
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable or api_key parameter required")
        
        self.max_iterations = max_iterations
        
        # Initialize all agents
        self.parser_agent = ParserAgent(api_key=self.api_key)
        self.jd_analyzer = JDAnalyzerAgent(api_key=self.api_key)
        self.gap_analyzer = GapAnalyzerAgent(api_key=self.api_key)
        self.rewrite_agent = RewriteAgent(api_key=self.api_key)
        self.consistency_checker = ConsistencyCheckerAgent(api_key=self.api_key)
        
        # Initialize LaTeX renderer
        self.latex_renderer = LaTeXRenderer()
    
    async def align_resume(self, request: AlignmentRequest) -> AlignmentResponse:
        """Execute the full alignment pipeline.
        
        Pipeline:
        1. JDAnalyzerAgent: Analyze job description
        2. GapAnalyzerAgent: Identify gaps in resume
        3. Refinement Loop (until ATS >= 95 or max iterations):
           a. RewriteAgent: Rewrite resume to address gaps
           b. ConsistencyCheckerAgent: Check ATS score and provide critique
           c. If ATS < 95, repeat with new critique
        4. Generate LaTeX PDF from final aligned resume
        
        Args:
            request: AlignmentRequest with resume and job description.
            
        Returns:
            AlignmentResponse: Aligned resume with changes, metrics, and PDF.
        """
        start_time = time.time()
        
        original_resume = request.resume
        job_description = request.job_description
        
        # Step 1: Analyze Job Description
        print("Step 1: Analyzing job description...")
        jd_analysis = await self.jd_analyzer.analyze(job_description)
        print(f"  - Identified {len(jd_analysis.get('must_have_skills', []))} must-have skills")
        print(f"  - Identified {len(jd_analysis.get('ats_keywords', []))} ATS keywords")
        
        # Step 2: Analyze Gaps
        print("\nStep 2: Analyzing gaps in resume...")
        gap_analysis = await self.gap_analyzer.analyze_gaps(
            resume=original_resume,
            job_description=job_description,
            jd_analysis=jd_analysis
        )
        initial_match = gap_analysis.get("overall_match_percentage", 0)
        print(f"  - Initial match: {initial_match}%")
        print(f"  - Missing {len(gap_analysis.get('missing_must_have_skills', []))} must-have skills")
        
        # Step 3: Refinement Loop
        print("\nStep 3: Starting refinement loop...")
        current_resume_draft = original_resume.model_dump(mode='json', exclude_none=True)
        all_changes: List[Dict[str, Any]] = []
        iteration = 0
        final_ats_score = 0.0
        final_keyword_score = 0.0
        
        while iteration < self.max_iterations:
            iteration += 1
            print(f"\n  Iteration {iteration}/{self.max_iterations}:")
            
            # 3a. Rewrite resume
            print("    - Rewriting resume...")
            rewrite_result = await self.rewrite_agent.rewrite(
                resume=self._dict_to_resume(current_resume_draft),
                gap_analysis=gap_analysis,
                jd_analysis=jd_analysis
            )
            
            # Extract updated resume and changes
            updated_resume_dict = rewrite_result.get("updated_resume", {})
            changes = rewrite_result.get("changes", [])
            all_changes.extend(changes)
            
            # Merge updated fields with current draft to preserve all required fields
            if updated_resume_dict:
                current_resume_draft.update(updated_resume_dict)
            
            print(f"    - Made {len(changes)} changes")
            
            # 3b. Check consistency and ATS score
            print("    - Checking ATS score...")
            consistency_result = await self.consistency_checker.check(
                resume_draft=updated_resume_dict,
                jd_analysis=jd_analysis
            )
            
            ats_score = consistency_result.get("ats_score", 0.0)
            keyword_score = consistency_result.get("keyword_match_score", 0.0)
            critique = consistency_result.get("critique", "")
            approved = consistency_result.get("approved", False)
            
            print(f"    - ATS Score: {ats_score:.1f}/100")
            print(f"    - Keyword Match: {keyword_score*100:.1f}%")
            
            # Update current draft
            current_resume_draft = updated_resume_dict
            final_ats_score = ats_score
            final_keyword_score = keyword_score
            
            # 3c. Check if approved or ATS >= 95
            if approved or ats_score >= 95.0:
                print(f"    ✓ ATS target reached! (Score: {ats_score:.1f})")
                break
            
            # Update gap analysis with critique for next iteration
            gap_analysis["critique"] = critique
            gap_analysis["missing_keywords"] = consistency_result.get("missing_keywords", [])
            gap_analysis["improvement_priority"] = consistency_result.get("improvement_priority", [])
            
            print(f"    - Critique: {critique[:100]}...")
        
        if iteration >= self.max_iterations:
            print(f"\n  Max iterations ({self.max_iterations}) reached. Final ATS: {final_ats_score:.1f}")
        
        # Convert final draft back to Resume object
        aligned_resume = self._dict_to_resume(current_resume_draft)
        
        # Step 4: Generate simple text/JSON output (LaTeX PDF generation is optional)
        print("\nStep 4: Preparing output...")
        pdf_url = None
        latex_source = None
        
        # Skip PDF generation for now - can be added later with proper LaTeX setup
        print("  - PDF generation skipped (LaTeX not configured)")
        
        # Build metrics
        processing_time = time.time() - start_time
        metrics = AlignmentMetrics(
            keyword_match_score=final_keyword_score,
            original_keyword_score=initial_match / 100.0,
            ats_score=final_ats_score,
            total_changes=len(all_changes),
            sections_modified=len(set(c.get("section", "") for c in all_changes)),
            iterations_count=iteration,
            avg_confidence=sum(c.get("confidence_score", 0.0) for c in all_changes) / max(len(all_changes), 1),
            processing_time_seconds=processing_time
        )
        
        # Convert changes to DiffObject list
        diff_objects = self._build_diff_objects(all_changes)
        
        # Build response
        response = AlignmentResponse(
            aligned_resume=aligned_resume,
            original_resume=original_resume,
            metrics=metrics,
            changes=diff_objects,
            template_id=template_id,
            latex_source=latex_source,
            pdf_url=pdf_url
        )
        
        print(f"\n✓ Alignment complete in {processing_time:.2f}s")
        print(f"  - Final ATS Score: {final_ats_score:.1f}/100")
        print(f"  - Keyword Match: {final_keyword_score*100:.1f}%")
        print(f"  - Total Changes: {len(all_changes)}")
        print(f"  - Iterations: {iteration}")
        
        return response
    
    async def parse_resume_text(self, resume_text: str) -> Resume:
        """Parse raw resume text into structured Resume object.
        
        Args:
            resume_text: Raw text from resume document.
            
        Returns:
            Resume: Structured resume object.
        """
        return await self.parser_agent.parse(resume_text)
    
    def _dict_to_resume(self, resume_dict: Dict[str, Any]) -> Resume:
        """Convert dictionary to Resume object with validation."""
        # Ensure full_name is present (required field)
        if "full_name" not in resume_dict:
            raise ValueError("Resume dictionary missing required field: full_name")
        
        # Convert nested structures with error handling
        if "experiences" in resume_dict and resume_dict["experiences"]:
            try:
                resume_dict["experiences"] = [
                    Experience(**exp) if isinstance(exp, dict) else exp 
                    for exp in resume_dict["experiences"]
                ]
            except Exception as e:
                print(f"Warning: Failed to parse experiences: {e}")
                resume_dict["experiences"] = []
        
        if "education" in resume_dict and resume_dict["education"]:
            try:
                resume_dict["education"] = [
                    Education(**edu) if isinstance(edu, dict) else edu
                    for edu in resume_dict["education"]
                ]
            except Exception as e:
                print(f"Warning: Failed to parse education: {e}")
                resume_dict["education"] = []
        
        if "projects" in resume_dict and resume_dict["projects"]:
            try:
                resume_dict["projects"] = [
                    Project(**proj) if isinstance(proj, dict) else proj
                    for proj in resume_dict["projects"]
                ]
            except Exception as e:
                print(f"Warning: Failed to parse projects: {e}")
                resume_dict["projects"] = []
        
        if "certifications" in resume_dict and resume_dict["certifications"]:
            try:
                resume_dict["certifications"] = [
                    Certification(**cert) if isinstance(cert, dict) else cert
                    for cert in resume_dict["certifications"]
                ]
            except Exception as e:
                print(f"Warning: Failed to parse certifications: {e}")
                resume_dict["certifications"] = []
        
        try:
            return Resume(**resume_dict)
        except Exception as e:
            raise ValueError(f"Failed to create Resume object: {e}\nResume dict keys: {list(resume_dict.keys())}")
    
    def _build_diff_objects(self, changes: List[Dict[str, Any]]) -> List[DiffObject]:
        """Convert change dicts to DiffObject list."""
        diff_objects = []
        
        for change in changes:
            try:
                change_type_str = change.get("change_type", "modified")
                change_type = ChangeType(change_type_str) if change_type_str in [e.value for e in ChangeType] else ChangeType.MODIFIED
                
                diff = DiffObject(
                    section=change.get("section", "unknown"),
                    field=change.get("field", "text"),
                    change_type=change_type,
                    original_value=change.get("original_value"),
                    new_value=change.get("new_value"),
                    reason=change.get("reason"),
                    confidence_score=change.get("confidence_score")
                )
                diff_objects.append(diff)
            except Exception as e:
                print(f"Warning: Failed to create DiffObject from change: {e}")
                continue
        
        return diff_objects

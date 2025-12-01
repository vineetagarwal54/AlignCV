"""Alignment request/response models for AlignCV."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from .resume import Resume
from .job_description import JobDescription


class ChangeType(str, Enum):
    """Types of changes made during alignment."""
    ADDED = "added"
    MODIFIED = "modified"
    REMOVED = "removed"
    REORDERED = "reordered"


class DiffObject(BaseModel):
    """Represents a single change/diff in the alignment process."""
    
    section: str = Field(..., description="Resume section affected (e.g., 'summary', 'experience[0]')")
    field: str = Field(..., description="Specific field changed")
    change_type: ChangeType = Field(..., description="Type of change")
    
    original_value: Optional[Any] = Field(None, description="Original text/value")
    new_value: Optional[Any] = Field(None, description="New text/value")
    
    reason: Optional[str] = Field(None, description="Why this change was made")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="AI confidence in this change")
    
    # LaTeX Template Support
    latex_anchor: Optional[str] = Field(
        None, 
        description="LaTeX anchor/command for this field (e.g., '\\experience[0].description')"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "section": "experiences[0].bullet_points[1]",
                "field": "text",
                "change_type": "modified",
                "original_value": "Built APIs using Python",
                "new_value": "Architected scalable RESTful APIs using Python and FastAPI",
                "reason": "Enhanced with keywords from JD: 'scalable', 'RESTful', 'FastAPI'",
                "confidence_score": 0.92
            }
        }


class AlignmentRequest(BaseModel):
    """Request model for resume alignment."""
    
    resume: Resume = Field(..., description="Parsed resume to align")
    job_description: JobDescription = Field(..., description="Target job description")
    
    # Alignment preferences
    preserve_structure: bool = Field(default=True, description="Keep original resume structure")
    preserve_formatting: bool = Field(default=True, description="Maintain original formatting")
    tone: Optional[str] = Field(default="professional", description="Desired tone (professional, casual, technical)")
    max_changes_per_section: Optional[int] = Field(default=None, description="Limit changes per section")
    
    # Advanced options
    include_missing_skills: bool = Field(default=True, description="Add missing relevant skills")
    reorder_bullets: bool = Field(default=False, description="Reorder bullets by relevance")
    use_rag_context: bool = Field(default=True, description="Use RAG for context-aware rewriting")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resume": {"full_name": "John Doe", "technical_skills": ["Python"]},
                "job_description": {"title": "Senior Backend Engineer"},
                "preserve_structure": True
            }
        }


class AlignmentMetrics(BaseModel):
    """Metrics about the alignment quality."""
    
    keyword_match_score: float = Field(..., ge=0.0, le=1.0, description="% of JD keywords in aligned resume")
    original_keyword_score: float = Field(..., ge=0.0, le=1.0, description="% of JD keywords in original resume")
    ats_score: float = Field(..., ge=0.0, le=100.0, description="ATS compatibility score (0-100)")
    total_changes: int = Field(..., description="Total number of changes made")
    sections_modified: int = Field(..., description="Number of sections modified")
    iterations_count: int = Field(default=1, description="Number of refinement iterations")
    
    avg_confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Average AI confidence")
    processing_time_seconds: Optional[float] = Field(None, description="Time taken for alignment")


class AlignmentResponse(BaseModel):
    """Response model for resume alignment."""
    
    aligned_resume: Resume = Field(..., description="Aligned/optimized resume")
    original_resume: Resume = Field(..., description="Original resume for comparison")
    metrics: AlignmentMetrics = Field(..., description="Alignment quality metrics")
    
    # Change tracking
    changes: List[DiffObject] = Field(default_factory=list, description="List of all changes made")
    
    # Metadata
    alignment_id: Optional[str] = Field(None, description="Unique ID for this alignment")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Layout preservation data (for frontend rendering)
    layout_metadata: Optional[Dict[str, Any]] = Field(
        None, 
        description="Original document layout info (fonts, spacing, structure)"
    )
    
    # LaTeX Template Support
    template_id: Optional[str] = Field(None, description="LaTeX template ID used for rendering")
    latex_source: Optional[str] = Field(None, description="Generated .tex source code")
    pdf_url: Optional[str] = Field(None, description="URL or path to compiled PDF output")
    
    class Config:
        json_schema_extra = {
            "example": {
                "aligned_resume": {"full_name": "John Doe"},
                "original_resume": {"full_name": "John Doe"},
                "changes": [],
                "metrics": {
                    "keyword_match_score": 0.85,
                    "original_keyword_score": 0.62,
                    "total_changes": 12,
                    "sections_modified": 3
                }
            }
        }


class AlignmentStatus(str, Enum):
    """Status of alignment job (for async processing)."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AlignmentJob(BaseModel):
    """Model for tracking async alignment jobs."""
    
    job_id: str = Field(..., description="Unique job identifier")
    status: AlignmentStatus = Field(default=AlignmentStatus.PENDING)
    
    request: AlignmentRequest = Field(..., description="Original request")
    response: Optional[AlignmentResponse] = Field(None, description="Result when completed")
    
    error_message: Optional[str] = Field(None, description="Error if failed")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(None)
    completed_at: Optional[datetime] = Field(None)

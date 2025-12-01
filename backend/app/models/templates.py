"""Resume template models for LaTeX rendering."""
from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ResumeTemplate(BaseModel):
    """LaTeX template configuration for resume rendering."""
    
    id: str = Field(..., description="Unique template identifier")
    name: str = Field(..., description="Human-readable template name")
    path: str = Field(..., description="Path to the .tex template file")
    field_to_anchor: Dict[str, str] = Field(
        ..., 
        description="Mapping from Resume model fields to LaTeX anchors (e.g., {'full_name': '<<NAME>>', 'email': '<<EMAIL>>'})"
    )
    
    engine: str = Field(default="pdflatex", description="Template engine (latex, pdflatex, xelatex)")
    
    # Optional metadata
    description: Optional[str] = Field(None, description="Template description")
    author: Optional[str] = Field(None, description="Template author")
    category: Optional[str] = Field(None, description="Template category (modern, classic, minimal, etc.)")
    preview_url: Optional[str] = Field(None, description="URL to template preview image")
    
    # Configuration
    requires_packages: list[str] = Field(
        default_factory=list, 
        description="LaTeX packages required by this template"
    )
    supports_sections: list[str] = Field(
        default_factory=lambda: ["experience", "education", "skills", "projects", "certifications"],
        description="Sections supported by this template"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether template is active/available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "modern-tech-1",
                "name": "Modern Tech Resume",
                "path": "templates/modern_tech.tex",
                "engine": "pdflatex",
                "field_to_anchor": {
                    "full_name": "<<NAME>>",
                    "email": "<<EMAIL>>",
                    "phone": "<<PHONE>>",
                    "summary": "<<SUMMARY>>",
                    "experiences": "<<EXPERIENCE>>",
                    "education": "<<EDUCATION>>",
                    "technical_skills": "<<SKILLS>>"
                },
                "requires_packages": ["geometry", "enumitem", "hyperref"],
                "category": "modern"
            }
        }

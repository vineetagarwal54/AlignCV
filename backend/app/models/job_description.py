"""Job Description models for AlignCV."""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class JobDescription(BaseModel):
    """Structured job description model."""
    
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    description: str = Field(..., description="Full job description text")
    
    location: Optional[str] = Field(None, description="Job location")
    job_type: Optional[str] = Field(None, description="Job type (Full-time, Part-time, Contract, etc.)")
    responsibilities: List[str] = Field(default_factory=list, description="List of key responsibilities")
    requirements: List[str] = Field(default_factory=list, description="List of requirements")
    preferred_qualifications: List[str] = Field(default_factory=list, description="Preferred qualifications")
    
    # Keywords and skills
    required_skills: List[str] = Field(default_factory=list, description="Required skills extracted from JD")
    preferred_skills: List[str] = Field(default_factory=list, description="Preferred skills extracted from JD")
    keywords: List[str] = Field(default_factory=list, description="Important keywords from JD")
    
    # Metadata
    salary_range: Optional[str] = Field(None, description="Salary range if provided")
    experience_level: Optional[str] = Field(None, description="Experience level (Entry, Mid, Senior, etc.)")
    industry: Optional[str] = Field(None, description="Industry sector")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('responsibilities', 'requirements', 'preferred_qualifications', mode='before')
    @classmethod
    def split_if_string(cls, v):
        """Convert string to list if needed."""
        if isinstance(v, str):
            return [item.strip() for item in v.split('\n') if item.strip()]
        return v
    
    @field_validator('required_skills', 'preferred_skills', 'keywords', mode='before')
    @classmethod
    def normalize_skills(cls, v):
        """Normalize and deduplicate skills."""
        if isinstance(v, str):
            v = [item.strip() for item in v.split(',') if item.strip()]
        # Deduplicate while preserving order
        seen = set()
        result = []
        for item in v:
            item_lower = item.lower()
            if item_lower not in seen:
                seen.add(item_lower)
                result.append(item)
        return result
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "location": "San Francisco, CA",
                "description": "We are looking for a Senior Software Engineer...",
                "required_skills": ["Python", "FastAPI", "Docker"],
                "experience_level": "Senior"
            }
        }

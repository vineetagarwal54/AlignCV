"""Resume models for AlignCV."""
from typing import List, Optional, Dict
from datetime import datetime, date
from pydantic import BaseModel, Field, field_validator, EmailStr


class Experience(BaseModel):
    """Work experience entry."""
    
    company: str = Field(..., description="Company name")
    title: str = Field(..., description="Job title")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[str] = Field(None, description="Start date (flexible format)")
    end_date: Optional[str] = Field(None, description="End date or 'Present'")
    is_current: bool = Field(default=False, description="Whether this is current role")
    
    description: Optional[str] = Field(None, description="Role description")
    bullet_points: List[str] = Field(default_factory=list, description="Achievement bullets")
    
    # Metadata
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    
    @field_validator('bullet_points', mode='before')
    @classmethod
    def split_bullets(cls, v):
        """Convert string to list if needed."""
        if isinstance(v, str):
            return [item.strip() for item in v.split('\n') if item.strip()]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "company": "Tech Corp",
                "title": "Software Engineer",
                "start_date": "Jan 2020",
                "end_date": "Present",
                "bullet_points": ["Built REST APIs", "Improved system performance by 50%"]
            }
        }


class Education(BaseModel):
    """Education entry."""
    
    institution: str = Field(..., description="School/University name")
    degree: str = Field(..., description="Degree type (BS, MS, PhD, etc.)")
    field_of_study: Optional[str] = Field(None, description="Major/Field of study")
    location: Optional[str] = Field(None, description="Location")
    graduation_date: Optional[str] = Field(None, description="Graduation date")
    gpa: Optional[str] = Field(None, description="GPA if relevant")
    honors: List[str] = Field(default_factory=list, description="Honors and awards")
    
    class Config:
        json_schema_extra = {
            "example": {
                "institution": "Stanford University",
                "degree": "Bachelor of Science",
                "field_of_study": "Computer Science",
                "graduation_date": "2020"
            }
        }


class Project(BaseModel):
    """Project entry."""
    
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL or GitHub link")
    bullet_points: List[str] = Field(default_factory=list, description="Project highlights")


class Certification(BaseModel):
    """Certification entry."""
    
    name: str = Field(..., description="Certification name")
    issuer: str = Field(..., description="Issuing organization")
    date_obtained: Optional[str] = Field(None, description="Date obtained")
    expiry_date: Optional[str] = Field(None, description="Expiry date if applicable")
    credential_id: Optional[str] = Field(None, description="Credential ID")


class Resume(BaseModel):
    """Structured resume model."""
    
    # Personal Information (only full_name is required)
    full_name: str = Field(..., description="Full name")
    email: Optional[EmailStr] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Current location")
    linkedin: Optional[str] = Field(None, description="LinkedIn URL")
    github: Optional[str] = Field(None, description="GitHub URL")
    website: Optional[str] = Field(None, description="Personal website")
    
    # Professional Summary
    summary: Optional[str] = Field(None, description="Professional summary/objective")
    
    # Experience
    experiences: List[Experience] = Field(default_factory=list, description="Work experience")
    
    # Education
    education: List[Education] = Field(default_factory=list, description="Education history")
    
    # Skills
    technical_skills: List[str] = Field(default_factory=list, description="Technical skills")
    soft_skills: List[str] = Field(default_factory=list, description="Soft skills")
    languages: List[str] = Field(default_factory=list, description="Languages spoken")
    
    # Additional Sections
    projects: List[Project] = Field(default_factory=list, description="Projects")
    certifications: List[Certification] = Field(default_factory=list, description="Certifications")
    publications: List[str] = Field(default_factory=list, description="Publications")
    awards: List[str] = Field(default_factory=list, description="Awards and honors")
    
    # Metadata
    total_years_experience: Optional[float] = Field(None, description="Total years of experience")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # LaTeX Template Support
    template_id: Optional[str] = Field(None, description="ID of the LaTeX template used")
    section_order: Optional[List[str]] = Field(None, description="Order of sections for rendering")
    latex_mapping: Optional[Dict[str, str]] = Field(
        None, 
        description="Mapping from Resume fields to LaTeX anchors (e.g., {'full_name': '\\name', 'summary': '\\summary'})"
    )
    
    @field_validator('technical_skills', 'soft_skills', 'languages', mode='before')
    @classmethod
    def normalize_lists(cls, v):
        """Normalize skill lists."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "email": "john@example.com",
                "summary": "Experienced software engineer...",
                "technical_skills": ["Python", "JavaScript", "SQL"],
                "experiences": []
            }
        }

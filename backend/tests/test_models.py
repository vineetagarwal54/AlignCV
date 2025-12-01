"""Simple tests for AlignCV models."""
import pytest
from app.models import (
    Resume, Experience, Education, Project,
    JobDescription, AlignmentRequest, AlignmentResponse,
    AlignmentMetrics, DiffObject, ChangeType, ResumeTemplate
)


def test_minimal_resume():
    """Test creating a minimal resume with only required fields."""
    resume = Resume(full_name="John Doe")
    
    assert resume.full_name == "John Doe"
    assert resume.email is None
    assert resume.experiences == []


def test_resume_with_data():
    """Test resume with optional fields."""
    resume = Resume(
        full_name="John Doe",
        email="john@example.com",
        phone="+1-555-0100",
        summary="Experienced software engineer",
        technical_skills=["Python", "FastAPI", "Docker"]
    )
    
    assert resume.full_name == "John Doe"
    assert resume.email == "john@example.com"
    assert len(resume.technical_skills) == 3


def test_resume_with_experience():
    """Test resume with work experience."""
    exp = Experience(
        company="Tech Corp",
        title="Software Engineer",
        bullet_points=["Built APIs", "Improved performance"]
    )
    
    resume = Resume(
        full_name="Jane Smith",
        experiences=[exp]
    )
    
    assert len(resume.experiences) == 1
    assert resume.experiences[0].company == "Tech Corp"


def test_resume_latex_fields():
    """Test LaTeX template fields on resume."""
    resume = Resume(
        full_name="John Doe",
        template_id="aligncv-1",
        section_order=["summary", "experience", "skills"],
        latex_mapping={"full_name": "<<NAME>>"}
    )
    
    assert resume.template_id == "aligncv-1"
    assert resume.section_order == ["summary", "experience", "skills"]
    assert resume.latex_mapping == {"full_name": "<<NAME>>"}


def test_minimal_job_description():
    """Test creating a minimal job description."""
    jd = JobDescription(
        title="Senior Backend Engineer",
        company="Tech Corp",
        description="We're looking for an experienced engineer..."
    )
    
    assert jd.title == "Senior Backend Engineer"
    assert jd.company == "Tech Corp"


def test_diff_object_with_latex_anchor():
    """Test DiffObject with LaTeX anchor."""
    diff = DiffObject(
        section="experiences[0].bullet_points[0]",
        field="text",
        change_type=ChangeType.MODIFIED,
        original_value="Built APIs",
        new_value="Architected scalable RESTful APIs",
        reason="Enhanced with JD keywords",
        confidence_score=0.92,
        latex_anchor="\\experience[0].bullet[0]"
    )
    
    assert diff.change_type == ChangeType.MODIFIED
    assert diff.latex_anchor == "\\experience[0].bullet[0]"


def test_alignment_metrics():
    """Test AlignmentMetrics creation."""
    metrics = AlignmentMetrics(
        keyword_match_score=0.85,
        original_keyword_score=0.62,
        total_changes=10,
        sections_modified=3
    )
    
    assert metrics.keyword_match_score == 0.85
    assert metrics.total_changes == 10


def test_alignment_response():
    """Test AlignmentResponse with LaTeX fields."""
    resume = Resume(full_name="John Doe")
    
    metrics = AlignmentMetrics(
        keyword_match_score=0.85,
        original_keyword_score=0.62,
        total_changes=10,
        sections_modified=3
    )
    
    response = AlignmentResponse(
        aligned_resume=resume,
        original_resume=resume,
        metrics=metrics,
        template_id="aligncv-1",
        latex_source="\\documentclass{article}...",
        pdf_url="/output/resume.pdf"
    )
    
    assert response.template_id == "aligncv-1"
    assert response.latex_source == "\\documentclass{article}..."
    assert response.pdf_url == "/output/resume.pdf"


def test_resume_template():
    """Test creating a resume template."""
    template = ResumeTemplate(
        id="aligncv-1",
        name="AlignCV Template",
        path="templates/aligncv_template.tex",
        field_to_anchor={
            "full_name": "<<NAME>>",
            "email": "<<EMAIL>>"
        }
    )
    
    assert template.id == "aligncv-1"
    assert template.engine == "pdflatex"  # default value
    assert len(template.field_to_anchor) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""Integration tests for the multi-agent alignment pipeline."""
import os
import pytest
from app.models.resume import Resume, Experience, Education
from app.models.job_description import JobDescription
from app.models.alignment import AlignmentRequest
from app.services.alignment_service import AlignmentService


# Skip tests if API key not available
pytestmark = pytest.mark.skipif(
    not os.getenv("GOOGLE_API_KEY"),
    reason="GOOGLE_API_KEY environment variable not set"
)


@pytest.fixture
def sample_resume():
    """Sample resume for testing."""
    return Resume(
        full_name="John Doe",
        email="john.doe@example.com",
        phone="+1-555-0100",
        location="San Francisco, CA",
        summary="Software engineer with 3 years of experience building web applications.",
        technical_skills=["Python", "JavaScript", "React", "SQL", "Git"],
        experiences=[
            Experience(
                company="Tech Startup Inc",
                position="Software Engineer",
                start_date="2021-06",
                end_date="Present",
                location="San Francisco, CA",
                bullet_points=[
                    "Built REST APIs using Python and Flask",
                    "Developed frontend components using React",
                    "Worked with PostgreSQL database"
                ]
            ),
            Experience(
                company="Web Agency LLC",
                position="Junior Developer",
                start_date="2020-01",
                end_date="2021-05",
                location="Remote",
                bullet_points=[
                    "Created websites for clients using JavaScript",
                    "Maintained existing codebases",
                    "Collaborated with design team"
                ]
            )
        ],
        education=[
            Education(
                institution="University of California",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2016-09",
                end_date="2020-05",
                gpa="3.7"
            )
        ]
    )


@pytest.fixture
def sample_job_description():
    """Sample job description for testing."""
    return JobDescription(
        title="Senior Backend Engineer",
        company="Fast Growth Startup",
        location="San Francisco, CA (Hybrid)",
        description="""
We're looking for a Senior Backend Engineer to join our team and help build scalable microservices.

You'll be working with Python, FastAPI, PostgreSQL, Docker, and Kubernetes to design and implement 
high-performance REST APIs. Experience with cloud platforms (AWS/GCP) and CI/CD pipelines is essential.

We value candidates who can mentor junior developers and contribute to architectural decisions.
""",
        requirements=[
            "5+ years of Python development experience",
            "Strong experience with FastAPI or similar frameworks",
            "Experience with Docker and Kubernetes",
            "Cloud platform experience (AWS or GCP)",
            "Strong understanding of microservices architecture"
        ],
        responsibilities=[
            "Design and implement scalable RESTful APIs",
            "Build microservices using Python and FastAPI",
            "Deploy and manage services on Kubernetes",
            "Mentor junior developers",
            "Contribute to technical architecture decisions"
        ],
        required_skills=["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL", "AWS"],
        nice_to_have=["GraphQL", "Redis", "Message queues", "CI/CD tools"]
    )


def test_alignment_service_initialization():
    """Test that AlignmentService can be initialized."""
    service = AlignmentService()
    assert service.max_iterations == 5
    assert service.parser_agent is not None
    assert service.jd_analyzer is not None
    assert service.gap_analyzer is not None
    assert service.rewrite_agent is not None
    assert service.consistency_checker is not None


def test_full_alignment_pipeline(sample_resume, sample_job_description):
    """Test the complete alignment pipeline end-to-end."""
    # Create alignment request
    request = AlignmentRequest(
        resume=sample_resume,
        job_description=sample_job_description,
        preserve_structure=True,
        preserve_formatting=True
    )
    
    # Run alignment
    service = AlignmentService(max_iterations=3)  # Limit iterations for testing
    response = service.align_resume(request)
    
    # Validate response structure
    assert response.aligned_resume is not None
    assert response.original_resume is not None
    assert response.metrics is not None
    assert response.changes is not None
    
    # Validate metrics
    assert 0 <= response.metrics.ats_score <= 100
    assert 0 <= response.metrics.keyword_match_score <= 1.0
    assert response.metrics.total_changes >= 0
    assert response.metrics.iterations_count >= 1
    assert response.metrics.iterations_count <= 3
    
    # Validate that some changes were made
    assert len(response.changes) > 0
    
    # Validate that aligned resume has same structure
    assert response.aligned_resume.full_name == sample_resume.full_name
    assert len(response.aligned_resume.experiences) == len(sample_resume.experiences)
    
    # Validate that keywords were added
    aligned_text = " ".join([
        exp.bullet_points[0] if exp.bullet_points else ""
        for exp in response.aligned_resume.experiences
    ])
    
    # Should have added some JD keywords
    jd_keywords = ["FastAPI", "scalable", "microservices", "Docker", "Kubernetes"]
    keyword_count = sum(1 for kw in jd_keywords if kw.lower() in aligned_text.lower())
    assert keyword_count > 0, "Expected some JD keywords to be added to resume"
    
    print(f"\n✓ Alignment test passed!")
    print(f"  ATS Score: {response.metrics.ats_score:.1f}/100")
    print(f"  Keyword Match: {response.metrics.keyword_match_score*100:.1f}%")
    print(f"  Changes: {response.metrics.total_changes}")
    print(f"  Iterations: {response.metrics.iterations_count}")


def test_parser_agent_basic():
    """Test basic resume parsing functionality."""
    service = AlignmentService()
    
    resume_text = """
John Smith
john.smith@email.com | +1-555-0199 | San Francisco, CA
LinkedIn: linkedin.com/in/johnsmith

SUMMARY
Experienced software engineer specializing in backend development.

SKILLS
Python, Django, PostgreSQL, Docker, AWS

EXPERIENCE
Senior Developer at Tech Corp (2019-Present)
- Developed microservices using Python and Django
- Managed PostgreSQL databases
- Deployed applications on AWS

EDUCATION
BS Computer Science, Stanford University, 2019
GPA: 3.8
"""
    
    resume = service.parse_resume_text(resume_text)
    
    # Validate parsed resume
    assert resume.full_name == "John Smith"
    assert resume.email == "john.smith@email.com"
    assert "Python" in resume.technical_skills
    assert len(resume.experiences) > 0
    assert len(resume.education) > 0
    
    print(f"\n✓ Parser test passed!")
    print(f"  Name: {resume.full_name}")
    print(f"  Skills: {len(resume.technical_skills)}")
    print(f"  Experiences: {len(resume.experiences)}")


def test_iterative_refinement():
    """Test that the refinement loop improves ATS score."""
    service = AlignmentService(max_iterations=5)
    
    # Simple resume with low keyword match
    basic_resume = Resume(
        full_name="Jane Developer",
        technical_skills=["Python"],
        experiences=[
            Experience(
                company="Startup",
                position="Developer",
                start_date="2020-01",
                end_date="Present",
                bullet_points=["Wrote code"]
            )
        ]
    )
    
    jd = JobDescription(
        title="Python Engineer",
        company="BigTech",
        description="Looking for Python expert with FastAPI, Docker, AWS experience. Build scalable APIs.",
        required_skills=["Python", "FastAPI", "Docker", "AWS"],
        requirements=["5+ years Python", "Microservices experience"],
        responsibilities=["Build scalable APIs", "Deploy on AWS"]
    )
    
    request = AlignmentRequest(resume=basic_resume, job_description=jd)
    response = service.align_resume(request)
    
    # Should have improved
    assert response.metrics.keyword_match_score > response.metrics.original_keyword_score
    assert response.metrics.ats_score > 0
    
    # Should have made changes
    assert len(response.changes) > 0
    
    print(f"\n✓ Refinement test passed!")
    print(f"  Original Match: {response.metrics.original_keyword_score*100:.1f}%")
    print(f"  Final Match: {response.metrics.keyword_match_score*100:.1f}%")
    print(f"  Improvement: {(response.metrics.keyword_match_score - response.metrics.original_keyword_score)*100:.1f}%")

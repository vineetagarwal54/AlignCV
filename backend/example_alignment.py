"""Example script demonstrating the multi-agent alignment pipeline."""
import os
from app.models.resume import Resume, Experience, Education
from app.models.job_description import JobDescription
from app.models.alignment import AlignmentRequest
from app.services.alignment_service import AlignmentService


def main():
    """Run example alignment."""
    
    # Check for API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nSet it with:")
        print("  export GOOGLE_API_KEY='your-api-key'  # Linux/Mac")
        print("  set GOOGLE_API_KEY=your-api-key       # Windows CMD")
        print("  $env:GOOGLE_API_KEY='your-api-key'    # Windows PowerShell")
        return
    
    print("=" * 70)
    print("AlignCV Multi-Agent Alignment Pipeline - Example")
    print("=" * 70)
    
    # Example 1: Create a sample resume
    print("\n📄 Creating sample resume...")
    resume = Resume(
        full_name="Alex Johnson",
        email="alex.johnson@example.com",
        phone="+1-555-0123",
        location="Seattle, WA",
        summary="Software engineer with 4 years of experience in web development.",
        technical_skills=["Python", "JavaScript", "React", "PostgreSQL", "Git"],
        experiences=[
            Experience(
                company="WebTech Solutions",
                position="Software Engineer",
                start_date="2021-03",
                end_date="Present",
                location="Seattle, WA",
                bullet_points=[
                    "Developed REST APIs using Python and Flask",
                    "Built frontend interfaces with React and TypeScript",
                    "Managed PostgreSQL databases with complex queries",
                    "Collaborated with team of 5 developers using Git"
                ]
            ),
            Experience(
                company="Digital Agency Co",
                position="Junior Developer",
                start_date="2020-01",
                end_date="2021-02",
                location="Remote",
                bullet_points=[
                    "Created responsive websites using JavaScript",
                    "Fixed bugs in existing codebases",
                    "Worked with designers on UI implementation"
                ]
            )
        ],
        education=[
            Education(
                institution="University of Washington",
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                start_date="2016-09",
                end_date="2020-06",
                gpa="3.6"
            )
        ]
    )
    print(f"  ✓ Resume created: {resume.full_name}")
    print(f"    Skills: {', '.join(resume.technical_skills[:3])}...")
    print(f"    Experience: {len(resume.experiences)} positions")
    
    # Example 2: Create target job description
    print("\n💼 Creating target job description...")
    job_description = JobDescription(
        title="Senior Backend Engineer",
        company="CloudScale Tech",
        location="Seattle, WA (Hybrid)",
        salary_range="$140k - $180k",
        description="""
CloudScale Tech is seeking a Senior Backend Engineer to join our platform team.

You will design and build scalable microservices using Python, FastAPI, and Docker.
Experience with Kubernetes, AWS, and CI/CD pipelines is required.

We're looking for someone who can architect high-performance APIs, mentor junior 
developers, and contribute to technical strategy.
""",
        requirements=[
            "5+ years of Python development experience",
            "Strong experience with FastAPI or similar async frameworks",
            "Hands-on experience with Docker and Kubernetes",
            "AWS cloud platform experience (EC2, S3, RDS)",
            "Understanding of microservices architecture",
            "Experience mentoring junior developers"
        ],
        responsibilities=[
            "Design and implement scalable RESTful APIs",
            "Build microservices using Python and FastAPI",
            "Deploy and manage services on Kubernetes clusters",
            "Implement CI/CD pipelines for automated deployments",
            "Mentor junior backend engineers",
            "Contribute to architectural decisions and tech strategy"
        ],
        required_skills=[
            "Python",
            "FastAPI",
            "Docker",
            "Kubernetes",
            "AWS",
            "PostgreSQL",
            "Redis",
            "CI/CD"
        ],
        nice_to_have=[
            "GraphQL",
            "Message queues (RabbitMQ/Kafka)",
            "Terraform",
            "Monitoring tools (Prometheus/Grafana)"
        ]
    )
    print(f"  ✓ Job description created: {job_description.title} at {job_description.company}")
    print(f"    Required skills: {', '.join(job_description.required_skills[:4])}...")
    print(f"    Seniority: Senior level (5+ years)")
    
    # Example 3: Create alignment request
    print("\n⚙️  Creating alignment request...")
    request = AlignmentRequest(
        resume=resume,
        job_description=job_description,
        preserve_structure=True,
        preserve_formatting=True,
        tone="professional",
        include_missing_skills=True,
        reorder_bullets=False,
        use_rag_context=False  # Not implemented yet
    )
    print("  ✓ Request configured with preservation settings")
    
    # Example 4: Run alignment pipeline
    print("\n🚀 Starting alignment pipeline...")
    print("   (This may take 30-60 seconds)\n")
    
    service = AlignmentService(max_iterations=5)
    response = service.align_resume(request)
    
    # Example 5: Display results
    print("\n" + "=" * 70)
    print("ALIGNMENT RESULTS")
    print("=" * 70)
    
    print(f"\n📊 Metrics:")
    print(f"  • ATS Score:           {response.metrics.ats_score:.1f}/100")
    print(f"  • Keyword Match:       {response.metrics.keyword_match_score*100:.1f}%")
    print(f"  • Original Match:      {response.metrics.original_keyword_score*100:.1f}%")
    print(f"  • Improvement:         +{(response.metrics.keyword_match_score - response.metrics.original_keyword_score)*100:.1f}%")
    print(f"  • Total Changes:       {response.metrics.total_changes}")
    print(f"  • Sections Modified:   {response.metrics.sections_modified}")
    print(f"  • Refinement Cycles:   {response.metrics.iterations_count}")
    print(f"  • Processing Time:     {response.metrics.processing_time_seconds:.1f}s")
    
    if response.changes:
        print(f"\n📝 Sample Changes (showing first 3):")
        for i, change in enumerate(response.changes[:3], 1):
            print(f"\n  {i}. Section: {change.section}")
            print(f"     Change Type: {change.change_type.value}")
            if change.original_value:
                print(f"     Before: {str(change.original_value)[:80]}...")
            if change.new_value:
                print(f"     After:  {str(change.new_value)[:80]}...")
            if change.reason:
                print(f"     Reason: {change.reason}")
            if change.confidence_score:
                print(f"     Confidence: {change.confidence_score:.0%}")
    
    print(f"\n📄 PDF Output:")
    if response.pdf_url:
        print(f"  ✓ Generated: {response.pdf_url}")
    else:
        print(f"  ⚠️  PDF generation skipped (LaTeX not installed)")
        print(f"     LaTeX source available in response.latex_source")
    
    # Example 6: Show aligned resume summary
    print(f"\n👤 Aligned Resume Summary:")
    print(f"  Name: {response.aligned_resume.full_name}")
    print(f"  Skills: {', '.join(response.aligned_resume.technical_skills[:5])}...")
    
    if response.aligned_resume.experiences:
        print(f"\n  First Experience (aligned):")
        exp = response.aligned_resume.experiences[0]
        print(f"  • {exp.position} at {exp.company}")
        print(f"  • Bullet points ({len(exp.bullet_points or [])}):")
        for bullet in (exp.bullet_points or [])[:2]:
            print(f"    - {bullet}")
    
    print("\n" + "=" * 70)
    print("✓ Alignment complete!")
    print("=" * 70)
    
    # Return response for further processing
    return response


if __name__ == "__main__":
    try:
        result = main()
        print("\n💡 Tip: Import this script and call main() to get the AlignmentResponse object")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

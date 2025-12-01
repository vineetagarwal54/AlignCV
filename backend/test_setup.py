"""Quick test script for AlignCV API."""
import os
import sys

print("=" * 70)
print("AlignCV API Test")
print("=" * 70)

# Check API key
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    print(f"✅ GOOGLE_API_KEY is set ({api_key[:10]}...)")
else:
    print("❌ GOOGLE_API_KEY not set!")
    print("\nSet it with:")
    print("  $env:GOOGLE_API_KEY='your-api-key'  # PowerShell")
    sys.exit(1)

# Check imports
print("\n" + "=" * 70)
print("Checking imports...")
print("=" * 70)

try:
    from fastapi import FastAPI
    print("✅ FastAPI")
except ImportError as e:
    print(f"❌ FastAPI: {e}")

try:
    import uvicorn
    print("✅ Uvicorn")
except ImportError as e:
    print(f"❌ Uvicorn: {e}")

try:
    import streamlit
    print("✅ Streamlit")
except ImportError as e:
    print(f"❌ Streamlit: {e}")

try:
    from app.models.resume import Resume
    print("✅ Resume model")
except ImportError as e:
    print(f"❌ Resume model: {e}")

try:
    from app.models.job_description import JobDescription
    print("✅ JobDescription model")
except ImportError as e:
    print(f"❌ JobDescription model: {e}")

try:
    from app.services.alignment_service import AlignmentService
    print("✅ AlignmentService")
except ImportError as e:
    print(f"❌ AlignmentService: {e}")

try:
    from google_adk import Agent, Gemini
    print("✅ google-adk")
except ImportError as e:
    print(f"❌ google-adk: {e}")
    print("\nInstall with: pip install google-adk")

# Test basic functionality
print("\n" + "=" * 70)
print("Testing basic functionality...")
print("=" * 70)

try:
    from app.models.resume import Resume, Experience
    
    # Create test resume
    resume = Resume(
        full_name="Test User",
        email="test@example.com",
        technical_skills=["Python", "FastAPI"],
        experiences=[
            Experience(
                company="Test Corp",
                position="Engineer",
                start_date="2020-01",
                end_date="Present",
                bullet_points=["Built APIs"]
            )
        ]
    )
    print("✅ Created test Resume object")
    
    # Create test JD
    from app.models.job_description import JobDescription
    jd = JobDescription(
        title="Senior Engineer",
        company="Test Inc",
        description="Looking for a senior engineer"
    )
    print("✅ Created test JobDescription object")
    
    # Create alignment request
    from app.models.alignment import AlignmentRequest
    request = AlignmentRequest(
        resume=resume,
        job_description=jd
    )
    print("✅ Created test AlignmentRequest object")
    
except Exception as e:
    print(f"❌ Error creating test objects: {e}")
    import traceback
    traceback.print_exc()

# Check if backend is running
print("\n" + "=" * 70)
print("Checking if backend is running...")
print("=" * 70)

try:
    import requests
    response = requests.get("http://localhost:8000/", timeout=2)
    if response.status_code == 200:
        print("✅ Backend API is running on http://localhost:8000")
        print(f"   Response: {response.json()}")
    else:
        print(f"⚠️  Backend responded with status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Backend is not running")
    print("\nStart it with:")
    print("  uvicorn main:app --reload")
except ImportError:
    print("⚠️  requests library not installed")
    print("   Install with: pip install requests")
except Exception as e:
    print(f"❌ Error checking backend: {e}")

print("\n" + "=" * 70)
print("Test Summary")
print("=" * 70)
print("\nIf all checks passed:")
print("  1. Start backend: uvicorn main:app --reload")
print("  2. Start Streamlit: streamlit run streamlit_app.py")
print("  3. Open browser: http://localhost:8501")
print("\nOr run the example:")
print("  python example_alignment.py")
print("\n" + "=" * 70)

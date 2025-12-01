"""FastAPI application for AlignCV resume alignment service."""
import os
import tempfile
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables from .env file
load_dotenv()

from app.models.resume import Resume
from app.models.job_description import JobDescription
from app.models.alignment import AlignmentRequest, AlignmentResponse
from app.services.alignment_service import AlignmentService
from app.services.document_parser import DocumentParser

app = FastAPI(
    title="AlignCV API",
    description="Multi-agent resume alignment service powered by Google Gemini",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
alignment_service = AlignmentService(max_iterations=3)
document_parser = DocumentParser()


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AlignCV API",
        "version": "1.0.0"
    }


@app.post("/api/parse/resume", response_model=Resume)
async def parse_resume(file: UploadFile = File(...)):
    """Parse uploaded resume file (PDF/DOCX) into structured Resume object.
    
    Args:
        file: Resume file (PDF or DOCX format)
        
    Returns:
        Resume: Structured resume data
    """
    if not file.filename.endswith(('.pdf', '.docx', '.doc')):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported"
        )
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract text
        raw_text, _ = document_parser.extract_raw_text(tmp_path)
        
        # Parse with AI
        resume = await alignment_service.parse_resume_text(raw_text)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return resume
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {str(e)}"
        )


@app.post("/api/align", response_model=AlignmentResponse)
async def align_resume(
    resume_file: UploadFile = File(...),
    job_title: str = Form(...),
    company: str = Form(...),
    job_description: str = Form(...),
    requirements: Optional[str] = Form(None),
    responsibilities: Optional[str] = Form(None),
    required_skills: Optional[str] = Form(None)
):
    """Align resume with job description and return aligned PDF.
    
    Args:
        resume_file: Resume PDF/DOCX file
        job_title: Job title
        company: Company name
        job_description: Full job description text
        requirements: Job requirements (optional, one per line)
        responsibilities: Job responsibilities (optional, one per line)
        required_skills: Required skills (optional, comma-separated)
        
    Returns:
        AlignmentResponse: Aligned resume with changes, metrics, and PDF URL
    """
    try:
        # 1. Parse resume
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(resume_file.filename).suffix) as tmp:
            content = await resume_file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        raw_text, _ = document_parser.extract_raw_text(tmp_path)
        resume = await alignment_service.parse_resume_text(raw_text)
        os.unlink(tmp_path)
        
        # 2. Create job description
        jd = JobDescription(
            title=job_title,
            company=company,
            description=job_description,
            requirements=[r.strip() for r in requirements.split('\n') if r.strip()] if requirements else [],
            responsibilities=[r.strip() for r in responsibilities.split('\n') if r.strip()] if responsibilities else [],
            required_skills=[s.strip() for s in required_skills.split(',') if s.strip()] if required_skills else []
        )
        
        # 3. Create alignment request
        request = AlignmentRequest(
            resume=resume,
            job_description=jd,
            preserve_structure=True,
            preserve_formatting=True
        )
        
        # 4. Run alignment
        response = await alignment_service.align_resume(request)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Alignment failed: {str(e)}"
        )


@app.get("/api/download/{filename}")
async def download_pdf(filename: str):
    """Download generated PDF resume.
    
    Args:
        filename: Name of the PDF file
        
    Returns:
        FileResponse: PDF file
    """
    # Look for PDF in common locations
    possible_paths = [
        Path(filename),
        Path("output") / filename,
        Path("pdfs") / filename,
        Path.cwd() / filename
    ]
    
    for pdf_path in possible_paths:
        if pdf_path.exists():
            return FileResponse(
                path=str(pdf_path),
                media_type="application/pdf",
                filename=filename
            )
    
    raise HTTPException(
        status_code=404,
        detail=f"PDF file not found: {filename}"
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

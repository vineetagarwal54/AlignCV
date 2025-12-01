# AlignCV - Quick Start Guide

## 🚀 Complete Testing Setup

This guide will help you test the AlignCV multi-agent resume alignment system.

---

## Prerequisites

✅ Python 3.10+ installed  
✅ Google API Key ([Get one here](https://aistudio.google.com/app/apikey))  
✅ Virtual environment activated  

---

## Step 1: Install Dependencies

```powershell
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Install all packages (FastAPI, Streamlit, google-adk, etc.)
pip install -r requirements.txt
```

---

## Step 2: Set API Key

```powershell
# Windows PowerShell
$env:GOOGLE_API_KEY='your-google-api-key-here'
```

---

## Step 3: Verify Setup

```bash
# Run setup test
python test_setup.py
```

Expected output:
```
✅ GOOGLE_API_KEY is set
✅ FastAPI
✅ Streamlit
✅ google-adk
✅ AlignmentService
✅ Created test Resume object
```

---

## Step 4: Start Backend API

**Terminal 1** - Start FastAPI backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Test it**: Open http://localhost:8000/docs in your browser

---

## Step 5: Start Streamlit App

**Terminal 2** - Start Streamlit UI:

```bash
streamlit run streamlit_app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

**Open it**: Go to http://localhost:8501

---

## Step 6: Test the Application

### Using Streamlit UI (Recommended)

1. **Open** http://localhost:8501 in your browser
2. **Upload** a resume (PDF or DOCX)
3. **Enter job details**:
   - Job Title: "Senior Backend Engineer"
   - Company: "Google"
   - Job Description: Paste a real job posting
4. **Click** "🚀 Align Resume"
5. **Wait** 30-60 seconds for AI processing
6. **View Results** in the "View Results" tab

### Using Python Script

```bash
# Run the example script
python example_alignment.py
```

### Using API Directly

```python
import requests

files = {
    'resume_file': ('resume.pdf', open('your_resume.pdf', 'rb'), 'application/pdf')
}

data = {
    'job_title': 'Senior Backend Engineer',
    'company': 'Google',
    'job_description': 'We are looking for...',
    'required_skills': 'Python, FastAPI, Docker'
}

response = requests.post('http://localhost:8000/api/align', files=files, data=data)
result = response.json()

print(f"ATS Score: {result['metrics']['ats_score']}")
```

---

## Expected Results

After alignment, you should see:

📊 **Metrics:**
- ATS Score: 90-98/100 ✅
- Keyword Match: 85-95%
- Total Changes: 10-25
- Iterations: 2-5

✏️ **Changes:**
- Original: "Built APIs using Python"
- Aligned: "Architected scalable RESTful APIs using Python and FastAPI"
- Reason: "Added keywords: scalable, RESTful, FastAPI"

📄 **Output:**
- Aligned Resume (JSON)
- PDF Resume (if LaTeX installed)
- LaTeX Source

---

## Testing Checklist

- [ ] Backend API starts successfully
- [ ] Streamlit app loads
- [ ] Can upload PDF/DOCX resume
- [ ] Can enter job description
- [ ] Alignment process completes
- [ ] ATS score ≥ 90
- [ ] Changes are displayed
- [ ] Can view results
- [ ] Metrics make sense

---

## Available Endpoints

### FastAPI Backend (http://localhost:8000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/parse/resume` | POST | Parse resume file → Resume object |
| `/api/align` | POST | Align resume with JD → PDF + changes |
| `/api/download/{filename}` | GET | Download generated PDF |
| `/docs` | GET | Interactive API documentation |

### Streamlit UI (http://localhost:8501)

- **Align Resume Tab**: Upload and align
- **View Results Tab**: See metrics and changes
- **Sidebar**: Instructions and info

---

## Troubleshooting

### ❌ "Cannot connect to API"

**Problem**: Streamlit can't reach backend

**Solution**: Make sure backend is running
```bash
uvicorn main:app --reload
```

### ❌ "GOOGLE_API_KEY not set"

**Problem**: API key missing

**Solution**: Set environment variable
```powershell
$env:GOOGLE_API_KEY='your-key'
```

### ❌ "Import google_adk could not be resolved"

**Problem**: google-adk not installed

**Solution**: Install package
```bash
pip install google-adk
```

### ❌ "PDF generation failed"

**Problem**: LaTeX not installed

**Solution**: This is optional. You'll still get:
- Aligned resume (JSON)
- LaTeX source code
- You can compile PDF manually later

### ⚠️ Low ATS scores

**Problem**: ATS score < 80

**Solutions**:
- Use a more detailed job description
- Ensure resume has relevant experience
- Add more keywords to JD
- Increase max_iterations in AlignmentService

---

## Performance Tips

### Faster Testing
- Use shorter resumes (1-2 pages)
- Reduce `max_iterations` to 3
- Use concise job descriptions

### Production Settings
- Use `max_iterations=5` (default)
- Enable caching for JD analysis
- Consider async processing for multiple resumes

---

## Sample Test Data

### Quick Test Resume

Create `test_resume.txt`:
```
John Doe
john@email.com | San Francisco, CA

SUMMARY
Software engineer with 3 years experience in web development.

SKILLS
Python, JavaScript, React, PostgreSQL, Git

EXPERIENCE
Software Engineer at Tech Corp (2021-Present)
- Developed REST APIs using Python and Flask
- Built frontend applications with React
- Managed PostgreSQL databases

EDUCATION
BS Computer Science, UC Berkeley, 2020
```

### Quick Test Job Description

```
Senior Backend Engineer at Google

We're looking for a Senior Backend Engineer to join our team.

Requirements:
- 5+ years Python development
- Experience with FastAPI or Django
- Strong knowledge of microservices architecture
- Docker and Kubernetes experience
- AWS or GCP cloud platform experience

Responsibilities:
- Design and implement scalable RESTful APIs
- Build microservices using Python
- Deploy services on Kubernetes
- Mentor junior engineers
```

---

## What to Expect

### During Alignment (30-60s)

You'll see in the terminal:
```
Step 1: Analyzing job description...
  - Identified 8 must-have skills
  - Identified 15 ATS keywords

Step 2: Analyzing gaps in resume...
  - Initial match: 65%
  - Missing 3 must-have skills

Step 3: Starting refinement loop...
  Iteration 1/5:
    - Rewriting resume...
    - Made 8 changes
    - Checking ATS score...
    - ATS Score: 78.0/100

  Iteration 2/5:
    - ATS Score: 88.5/100

  Iteration 3/5:
    - ATS Score: 96.0/100
    ✓ ATS target reached!

✓ Alignment complete in 42.3s
```

### In Streamlit UI

- Loading spinner: "AI agents are analyzing..."
- Success message + balloons 🎈
- Metrics cards with scores
- List of changes made
- Download buttons for PDF/LaTeX

---

## Next Steps

After successful testing:

1. **Review aligned resume** for accuracy
2. **Test with different resumes** and job descriptions
3. **Adjust settings** if needed (max_iterations, etc.)
4. **Deploy to production** (optional)
5. **Add authentication** (optional)
6. **Integrate with frontend** (React Native)

---

## Additional Resources

📖 **Documentation:**
- `TESTING_GUIDE.md` - Detailed testing instructions
- `IMPLEMENTATION_SUMMARY.md` - Architecture details
- API docs: http://localhost:8000/docs

🧪 **Testing:**
- `test_setup.py` - Verify installation
- `example_alignment.py` - Complete example
- `tests/test_alignment_pipeline.py` - Unit tests

🔧 **Configuration:**
- `requirements.txt` - All dependencies
- `main.py` - FastAPI endpoints
- `streamlit_app.py` - Web UI
- `app/services/alignment_service.py` - Core logic

---

## Quick Commands Reference

```bash
# Setup
.\myenv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GOOGLE_API_KEY='your-key'

# Test setup
python test_setup.py

# Run backend
uvicorn main:app --reload

# Run Streamlit (in another terminal)
streamlit run streamlit_app.py

# Run example
python example_alignment.py

# Run tests
pytest tests/test_alignment_pipeline.py -v
```

---

## Support

For issues:
1. Check `TESTING_GUIDE.md` troubleshooting section
2. Review terminal logs for errors
3. Verify API key is set correctly
4. Check http://localhost:8000/docs for API status

---

**You're ready to test! 🎉**

Start with: `python test_setup.py`

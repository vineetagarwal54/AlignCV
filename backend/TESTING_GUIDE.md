# Testing Guide for AlignCV

## Quick Start Testing

### 1. Install Dependencies

```bash
# Activate virtual environment
.\myenv\Scripts\Activate.ps1

# Install all dependencies (including streamlit)
pip install -r requirements.txt
```

### 2. Set API Key

```powershell
# Windows PowerShell
$env:GOOGLE_API_KEY='your-google-api-key-here'
```

### 3. Start the Backend API

```bash
# Terminal 1 - Start FastAPI backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 4. Start the Streamlit App

```bash
# Terminal 2 - Start Streamlit UI
streamlit run streamlit_app.py
```

Expected output:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### 5. Test the Application

1. **Open browser**: Go to `http://localhost:8501`
2. **Upload resume**: Choose a PDF or DOCX file
3. **Enter job details**:
   - Job Title: "Senior Backend Engineer"
   - Company: "Google"
   - Job Description: Paste a real job posting
4. **Click "Align Resume"**
5. **View results** in the "View Results" tab

---

## API Testing (Manual)

### Test API Endpoints with curl

#### 1. Health Check
```bash
curl http://localhost:8000/
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AlignCV API",
  "version": "1.0.0"
}
```

#### 2. Parse Resume
```bash
curl -X POST http://localhost:8000/api/parse/resume \
  -F "file=@path/to/your/resume.pdf"
```

#### 3. Align Resume
```bash
curl -X POST http://localhost:8000/api/align \
  -F "resume_file=@path/to/resume.pdf" \
  -F "job_title=Senior Backend Engineer" \
  -F "company=Google" \
  -F "job_description=We are looking for a Senior Backend Engineer..." \
  -F "required_skills=Python, FastAPI, Docker"
```

---

## Testing with Python Requests

Create `test_api.py`:

```python
import requests

API_URL = "http://localhost:8000"

# Test health check
response = requests.get(f"{API_URL}/")
print("Health:", response.json())

# Test alignment
files = {
    'resume_file': ('resume.pdf', open('path/to/resume.pdf', 'rb'), 'application/pdf')
}

data = {
    'job_title': 'Senior Backend Engineer',
    'company': 'Google',
    'job_description': '''
    We are looking for a Senior Backend Engineer to build scalable APIs.
    
    Requirements:
    - 5+ years Python experience
    - Experience with FastAPI, Docker, Kubernetes
    - Strong knowledge of microservices
    ''',
    'requirements': '5+ years Python\nFastAPI experience\nDocker and Kubernetes',
    'required_skills': 'Python, FastAPI, Docker, Kubernetes, AWS'
}

response = requests.post(f"{API_URL}/api/align", files=files, data=data)
result = response.json()

print(f"ATS Score: {result['metrics']['ats_score']}")
print(f"Changes: {result['metrics']['total_changes']}")
print(f"Iterations: {result['metrics']['iterations_count']}")
```

Run:
```bash
python test_api.py
```

---

## Unit Tests

### Run Existing Tests

```bash
# Run all tests
pytest tests/ -v

# Run alignment pipeline tests
pytest tests/test_alignment_pipeline.py -v

# Run with output
pytest tests/test_alignment_pipeline.py -v -s
```

### Run Specific Test

```bash
# Test full alignment pipeline
pytest tests/test_alignment_pipeline.py::test_full_alignment_pipeline -v

# Test parser
pytest tests/test_alignment_pipeline.py::test_parser_agent_basic -v
```

---

## Example Test Flow

### Complete Test Scenario

1. **Prepare test resume** (save as `test_resume.pdf`):
```
John Doe
john.doe@email.com | San Francisco, CA

SUMMARY
Software engineer with 3 years of experience building web applications.

SKILLS
Python, JavaScript, React, SQL, Git

EXPERIENCE
Software Engineer at Tech Startup Inc (2021-Present)
- Built REST APIs using Python and Flask
- Developed frontend with React
- Managed PostgreSQL databases

EDUCATION
BS Computer Science, UC Berkeley, 2020
```

2. **Create test job description**:
```
Senior Backend Engineer at Google

We're looking for a Senior Backend Engineer to join our Cloud Platform team.

Requirements:
- 5+ years Python development
- Experience with FastAPI or Django
- Strong knowledge of microservices
- Docker and Kubernetes experience
- AWS or GCP cloud platforms

Responsibilities:
- Design and build scalable RESTful APIs
- Implement microservices architecture
- Deploy services on Kubernetes
- Mentor junior engineers
```

3. **Test via Streamlit**:
   - Upload `test_resume.pdf`
   - Paste job description
   - Add requirements and skills
   - Click "Align Resume"
   - Review results

4. **Expected Results**:
   - ATS Score: 90-98/100
   - Keyword Match: 85-95%
   - Total Changes: 10-20
   - Iterations: 2-4

---

## Troubleshooting

### Backend won't start

**Error**: `ImportError: cannot import name 'Agent' from 'google_adk'`

**Solution**: Check google-adk installation
```bash
pip install google-adk
```

### API returns 500 error

**Error**: `GOOGLE_API_KEY environment variable not set`

**Solution**: Set the API key
```powershell
$env:GOOGLE_API_KEY='your-api-key'
```

### Streamlit can't connect to API

**Error**: "Cannot connect to API"

**Solution**: Make sure backend is running
```bash
# Terminal 1
uvicorn main:app --reload
```

### PDF generation fails

**Error**: "PDF generation failed"

**Solution**: LaTeX is optional. The API will still return:
- `pdf_url`: null
- `latex_source`: LaTeX source code (you can compile manually)

### Tests are skipped

**Error**: "GOOGLE_API_KEY environment variable not set"

**Solution**: Set API key before running tests
```powershell
$env:GOOGLE_API_KEY='your-api-key'
pytest tests/test_alignment_pipeline.py -v
```

---

## Performance Testing

### Test Response Times

```python
import time
import requests

API_URL = "http://localhost:8000"

# Measure alignment time
start = time.time()
response = requests.post(f"{API_URL}/api/align", files=files, data=data)
elapsed = time.time() - start

print(f"Total time: {elapsed:.2f}s")
print(f"API processing: {response.json()['metrics']['processing_time_seconds']:.2f}s")
```

Expected times:
- Parse resume: 5-10s
- Full alignment: 30-60s
- Download PDF: <1s

---

## Interactive Testing (Streamlit)

### Features to Test

1. **Upload Resume**
   - ✅ PDF upload works
   - ✅ DOCX upload works
   - ✅ File name displayed
   - ❌ Invalid file rejected

2. **Job Details Form**
   - ✅ All required fields validated
   - ✅ Optional fields expandable
   - ✅ Multi-line inputs work

3. **Alignment Process**
   - ✅ Loading spinner shows
   - ✅ Progress messages appear
   - ✅ Success message on completion
   - ✅ Balloons animation

4. **Results Display**
   - ✅ Metrics cards show correct values
   - ✅ Progress bars update
   - ✅ Changes list displays
   - ✅ Before/after comparison works

5. **Download**
   - ✅ PDF download button (if LaTeX installed)
   - ✅ LaTeX source download
   - ✅ Files have correct names

---

## API Documentation

Once backend is running, visit:

**Swagger UI**: http://localhost:8000/docs

**ReDoc**: http://localhost:8000/redoc

These provide:
- Interactive API testing
- Request/response schemas
- Example requests
- Try-it-out functionality

---

## Sample Test Data

### Minimal Test

**Resume**: "John Doe, Software Engineer, Python experience"

**JD**: "Looking for Python developer with 2+ years experience"

**Expected**: ATS ~70-80, few changes

### Realistic Test

**Resume**: Full resume with 2-3 work experiences, education, skills

**JD**: Complete job posting with requirements, responsibilities, skills

**Expected**: ATS 90-98, 10-25 changes

### Stress Test

**Resume**: Long resume with 10+ years experience, many projects

**JD**: Detailed senior-level position with 20+ requirements

**Expected**: ATS 85-95, 25+ changes, longer processing time

---

## Quick Testing Checklist

- [ ] Backend starts without errors
- [ ] Streamlit app loads
- [ ] Can upload PDF resume
- [ ] Can enter job details
- [ ] Alignment completes successfully
- [ ] Results page shows metrics
- [ ] ATS score ≥ 90
- [ ] Changes list displays
- [ ] Can download outputs
- [ ] API documentation accessible

---

## Next Steps After Testing

1. **Validate results**: Review aligned resume for accuracy
2. **Test different resumes**: Try various formats and content
3. **Test different JDs**: Various industries and levels
4. **Performance tuning**: Adjust max_iterations if needed
5. **Deploy**: Consider Docker containerization
6. **Monitor**: Add logging and analytics

---

## Support

### Logs

**Backend logs**: Check terminal running uvicorn

**Streamlit logs**: Check terminal running streamlit

**API errors**: Visit http://localhost:8000/docs and test endpoints

### Common Issues

| Issue | Solution |
|-------|----------|
| API not responding | Restart uvicorn |
| Streamlit frozen | Refresh browser |
| Low ATS scores | Check JD has enough keywords |
| Alignment timeout | Reduce max_iterations |
| Import errors | Reinstall requirements.txt |

---

**Ready to test! 🚀**

Start both servers and open http://localhost:8501

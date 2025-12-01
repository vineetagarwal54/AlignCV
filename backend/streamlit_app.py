"""Streamlit web app for AlignCV resume alignment."""
import streamlit as st
import requests
import os
from pathlib import Path
import tempfile

# Page config
st.set_page_config(
    page_title="AlignCV - Resume Alignment",
    page_icon="📄",
    layout="wide"
)

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Title
st.title("📄 AlignCV - AI-Powered Resume Alignment")
st.markdown("**Optimize your resume for any job using multi-agent AI**")

# Check API health
try:
    health = requests.get(f"{API_URL}/", timeout=2)
    if health.status_code == 200:
        st.success("✅ API is running")
    else:
        st.error("❌ API is not responding correctly")
except:
    st.error("❌ Cannot connect to API. Make sure the backend is running on port 8000")
    st.code("Run: uvicorn main:app --reload")

st.markdown("---")

# Create tabs
tab1, tab2 = st.tabs(["🎯 Align Resume", "📊 View Results"])

with tab1:
    st.header("Upload Resume & Job Description")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Your Resume")
        resume_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your current resume"
        )
        
        if resume_file:
            st.success(f"✓ Uploaded: {resume_file.name}")
    
    with col2:
        st.subheader("💼 Target Job")
        job_title = st.text_input(
            "Job Title",
            placeholder="e.g., Senior Backend Engineer",
            help="The position you're applying for"
        )
        
        company = st.text_input(
            "Company Name",
            placeholder="e.g., Google",
            help="Company name"
        )
    
    st.markdown("---")
    
    job_description = st.text_area(
        "Job Description",
        height=200,
        placeholder="""Paste the full job description here...

Example:
We're looking for a Senior Backend Engineer to join our team...
        """,
        help="Paste the complete job posting"
    )
    
    # Optional fields (expandable)
    with st.expander("➕ Add More Details (Optional)"):
        requirements = st.text_area(
            "Requirements (one per line)",
            height=100,
            placeholder="""5+ years Python experience
Experience with FastAPI
Strong knowledge of microservices""",
            help="List specific requirements from the job posting"
        )
        
        responsibilities = st.text_area(
            "Responsibilities (one per line)",
            height=100,
            placeholder="""Design scalable APIs
Build microservices
Mentor junior developers""",
            help="Key responsibilities from the job posting"
        )
        
        required_skills = st.text_input(
            "Required Skills (comma-separated)",
            placeholder="Python, FastAPI, Docker, Kubernetes, AWS",
            help="Technical skills required"
        )
    
    st.markdown("---")
    
    # Alignment button
    if st.button("🚀 Align Resume", type="primary", use_container_width=True):
        if not resume_file:
            st.error("❌ Please upload a resume")
        elif not job_title:
            st.error("❌ Please enter job title")
        elif not company:
            st.error("❌ Please enter company name")
        elif not job_description:
            st.error("❌ Please enter job description")
        else:
            with st.spinner("🤖 AI agents are analyzing and aligning your resume..."):
                try:
                    # Prepare form data
                    files = {
                        'resume_file': (resume_file.name, resume_file.getvalue(), resume_file.type)
                    }
                    
                    data = {
                        'job_title': job_title,
                        'company': company,
                        'job_description': job_description,
                        'requirements': requirements if requirements else '',
                        'responsibilities': responsibilities if responsibilities else '',
                        'required_skills': required_skills if required_skills else ''
                    }
                    
                    # Call API with extended timeout
                    response = requests.post(
                        f"{API_URL}/api/align",
                        files=files,
                        data=data,
                        timeout=300  # 5 minutes for multi-agent processing
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state['alignment_result'] = result
                        st.success("✅ Resume aligned successfully!")
                        st.balloons()
                        
                        # Switch to results tab
                        st.info("👉 Check the 'View Results' tab to see your aligned resume")
                    else:
                        st.error(f"❌ Alignment failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.exception(e)

with tab2:
    st.header("📊 Alignment Results")
    
    if 'alignment_result' not in st.session_state:
        st.info("👈 Go to 'Align Resume' tab to align your resume first")
    else:
        result = st.session_state['alignment_result']
        metrics = result['metrics']
        
        # Metrics cards
        st.subheader("📈 Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ats_score = metrics['ats_score']
            ats_color = "green" if ats_score >= 95 else "orange" if ats_score >= 80 else "red"
            st.metric(
                "ATS Score",
                f"{ats_score:.1f}/100",
                delta=f"{ats_score - 70:.1f}" if ats_score > 70 else None
            )
            st.markdown(f":{ats_color}[{'🎯 Excellent!' if ats_score >= 95 else '⚠️ Good' if ats_score >= 80 else '❌ Needs work'}]")
        
        with col2:
            keyword_match = metrics['keyword_match_score'] * 100
            st.metric(
                "Keyword Match",
                f"{keyword_match:.1f}%",
                delta=f"+{(metrics['keyword_match_score'] - metrics['original_keyword_score']) * 100:.1f}%"
            )
        
        with col3:
            st.metric(
                "Changes Made",
                metrics['total_changes'],
                delta=None
            )
        
        with col4:
            st.metric(
                "Iterations",
                metrics['iterations_count'],
                delta=None
            )
        
        st.markdown("---")
        
        # Progress bars
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original vs Aligned")
            st.progress(metrics['original_keyword_score'], text=f"Original: {metrics['original_keyword_score']*100:.0f}%")
            st.progress(metrics['keyword_match_score'], text=f"Aligned: {metrics['keyword_match_score']*100:.0f}%")
        
        with col2:
            st.subheader("Processing Stats")
            st.write(f"⏱️ Processing time: {metrics['processing_time_seconds']:.1f}s")
            st.write(f"📝 Sections modified: {metrics['sections_modified']}")
            st.write(f"🎯 Avg confidence: {metrics.get('avg_confidence', 0)*100:.0f}%")
        
        st.markdown("---")
        
        # Changes details
        st.subheader("✏️ Changes Made")
        changes = result.get('changes', [])
        
        if changes:
            st.write(f"Showing {len(changes)} changes:")
            
            for i, change in enumerate(changes[:10], 1):  # Show first 10
                with st.expander(f"Change {i}: {change['section']} - {change['change_type']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Before:**")
                        st.text_area(
                            "Original",
                            value=str(change.get('original_value', 'N/A')),
                            height=100,
                            key=f"before_{i}",
                            disabled=True
                        )
                    
                    with col2:
                        st.markdown("**After:**")
                        st.text_area(
                            "New",
                            value=str(change.get('new_value', 'N/A')),
                            height=100,
                            key=f"after_{i}",
                            disabled=True
                        )
                    
                    if change.get('reason'):
                        st.info(f"💡 Reason: {change['reason']}")
                    
                    if change.get('confidence_score'):
                        st.caption(f"Confidence: {change['confidence_score']*100:.0f}%")
            
            if len(changes) > 10:
                st.info(f"... and {len(changes) - 10} more changes")
        else:
            st.info("No changes were made")
        
        st.markdown("---")
        
        # Aligned resume preview
        st.subheader("📄 Aligned Resume")
        aligned_resume = result['aligned_resume']
        
        with st.expander("View Aligned Resume Data", expanded=False):
            st.json(aligned_resume)
        
        # Download section
        st.markdown("---")
        st.subheader("📥 Download")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Generate a formatted text version of the aligned resume
            aligned_resume_text = f"""
{result['aligned_resume']['full_name']}
{result['aligned_resume'].get('email', '')} | {result['aligned_resume'].get('phone', '')}
{result['aligned_resume'].get('location', '')}
LinkedIn: {result['aligned_resume'].get('linkedin', '')}

SUMMARY
{result['aligned_resume'].get('summary', 'N/A')}

SKILLS
{', '.join(result['aligned_resume'].get('skills', []))}

EXPERIENCE
"""
            for exp in result['aligned_resume'].get('experience', []):
                aligned_resume_text += f"\n{exp['title']} at {exp['company']}\n"
                aligned_resume_text += f"{exp.get('start_date', '')} - {exp.get('end_date', 'Present')}\n"
                for achievement in exp.get('achievements', []):
                    aligned_resume_text += f"• {achievement}\n"
            
            aligned_resume_text += "\nEDUCATION\n"
            for edu in result['aligned_resume'].get('education', []):
                aligned_resume_text += f"\n{edu['degree']} - {edu['institution']}\n"
                aligned_resume_text += f"Graduated: {edu.get('graduation_date', 'N/A')}\n"
                if edu.get('gpa'):
                    aligned_resume_text += f"GPA: {edu['gpa']}\n"
            
            st.download_button(
                label="📄 Download Aligned Resume (TXT)",
                data=aligned_resume_text,
                file_name="aligned_resume.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            if result.get('pdf_url'):
                st.info("💡 PDF generation requires LaTeX installation")
        
        with col2:
            if result.get('latex_source'):
                st.download_button(
                    label="📝 Download LaTeX Source",
                    data=result['latex_source'],
                    file_name="aligned_resume.tex",
                    mime="text/plain",
                    use_container_width=True
                )

# Sidebar
with st.sidebar:
    st.header("ℹ️ About AlignCV")
    st.markdown("""
    AlignCV uses a **multi-agent AI system** to optimize your resume for specific jobs.
    
    ### How it works:
    1. 🤖 **ParserAgent** extracts your resume data
    2. 🔍 **JDAnalyzerAgent** analyzes the job description
    3. 📊 **GapAnalyzerAgent** finds missing keywords
    4. ✍️ **RewriteAgent** enhances your resume
    5. ✅ **ConsistencyChecker** validates ATS score
    
    The system iterates until achieving **ATS score ≥ 95** or max iterations.
    
    ### Features:
    - ✅ Maintains truthfulness
    - ✅ Preserves your resume structure
    - ✅ Adds relevant keywords
    - ✅ Optimizes for ATS systems
    - ✅ Tracks all changes
    
    ---
    
    ### Setup:
    1. Set `OPENAI_API_KEY` environment variable
    2. Run backend: `uvicorn main:app --reload`
    3. Run this app: `streamlit run streamlit_app.py`
    """)
    
    st.markdown("---")
    st.caption("Powered by OpenAI GPT-4o-mini")

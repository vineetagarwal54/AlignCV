"""LaTeX rendering service for resume PDF generation."""
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
import logging

from jinja2 import Environment, FileSystemLoader, Template
from jinja2.exceptions import TemplateError

from ..models.resume import Resume, Experience, Education, Project, Certification
from ..models.templates import ResumeTemplate


logger = logging.getLogger(__name__)


class LaTeXRenderError(Exception):
    """Exception raised when LaTeX rendering fails."""
    pass


class LaTeXRenderer:
    """Service for rendering resumes using LaTeX templates."""
    
    def __init__(self, templates_dir: str = "templates", output_dir: str = "output"):
        """
        Initialize the LaTeX renderer.
        
        Args:
            templates_dir: Directory containing .tex template files
            output_dir: Directory for compiled PDF outputs
        """
        self.templates_dir = Path(templates_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment for LaTeX
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            line_statement_prefix='%%',
            line_comment_prefix='%#',
            trim_blocks=True,
            autoescape=False,
        )
    
    def render_resume(
        self,
        resume: Resume,
        template: ResumeTemplate,
        output_filename: Optional[str] = None
    ) -> Tuple[str, str, Optional[str]]:
        """
        Render a resume to PDF using a LaTeX template.
        
        Args:
            resume: Structured resume data
            template: Template configuration
            output_filename: Optional custom filename (without extension)
            
        Returns:
            Tuple of (tex_path, pdf_path, compilation_log)
            
        Raises:
            LaTeXRenderError: If rendering or compilation fails
        """
        if not output_filename:
            output_filename = f"resume_{resume.full_name.replace(' ', '_').lower()}"
        
        # Build template context from resume data
        context = self._build_template_context(resume, template)
        
        # Generate .tex file
        tex_source = self._fill_template(template, context)
        
        # Write .tex file
        tex_path = self.output_dir / f"{output_filename}.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(tex_source)
        
        logger.info(f"Generated LaTeX source: {tex_path}")
        
        # Compile to PDF
        pdf_path, compile_log = self._compile_latex(tex_path, template.engine)
        
        return str(tex_path), str(pdf_path), compile_log
    
    def _build_template_context(
        self,
        resume: Resume,
        template: ResumeTemplate
    ) -> Dict[str, Any]:
        """
        Build Jinja2 context from Resume model and template mapping.
        
        Args:
            resume: Resume data
            template: Template configuration with field_to_anchor mapping
            
        Returns:
            Context dictionary for Jinja2 template
        """
        # Base context with all resume fields
        context = {
            # Personal info
            'name': resume.full_name,
            'email': resume.email or '',
            'phone': resume.phone or '',
            'location': resume.location or '',
            'linkedin': resume.linkedin or '',
            'github': resume.github or '',
            'website': resume.website or '',
            
            # Summary
            'summary': resume.summary or '',
            
            # Experiences
            'experiences': [
                {
                    'company': exp.company,
                    'title': exp.title,
                    'location': exp.location or '',
                    'start_date': exp.start_date or '',
                    'end_date': exp.end_date or 'Present' if exp.is_current else exp.end_date or '',
                    'description': exp.description or '',
                    'bullets': exp.bullet_points,
                    'technologies': exp.technologies,
                }
                for exp in resume.experiences
            ],
            
            # Education
            'education': [
                {
                    'institution': edu.institution,
                    'degree': edu.degree,
                    'field': edu.field_of_study or '',
                    'location': edu.location or '',
                    'graduation_date': edu.graduation_date or '',
                    'gpa': edu.gpa or '',
                    'honors': edu.honors,
                }
                for edu in resume.education
            ],
            
            # Skills
            'technical_skills': resume.technical_skills,
            'soft_skills': resume.soft_skills,
            'languages': resume.languages,
            'skills_combined': resume.technical_skills + resume.soft_skills,
            
            # Projects
            'projects': [
                {
                    'name': proj.name,
                    'description': proj.description,
                    'technologies': proj.technologies,
                    'url': proj.url or '',
                    'bullets': proj.bullet_points,
                }
                for proj in resume.projects
            ],
            
            # Certifications
            'certifications': [
                {
                    'name': cert.name,
                    'issuer': cert.issuer,
                    'date': cert.date_obtained or '',
                    'expiry': cert.expiry_date or '',
                    'credential_id': cert.credential_id or '',
                }
                for cert in resume.certifications
            ],
            
            # Other sections
            'publications': resume.publications,
            'awards': resume.awards,
            
            # Section order (if specified)
            'section_order': resume.section_order or [
                'summary', 'experience', 'education', 
                'skills', 'projects', 'certifications'
            ],
        }
        
        # Apply custom latex_mapping if provided on resume
        if resume.latex_mapping:
            for field, anchor in resume.latex_mapping.items():
                # Get value from resume
                value = getattr(resume, field, None)
                if value is not None:
                    # Use anchor as key in context
                    context[anchor.strip('\\\\')] = value
        
        return context
    
    def _fill_template(
        self,
        template: ResumeTemplate,
        context: Dict[str, Any]
    ) -> str:
        """
        Fill LaTeX template with context data using Jinja2.
        
        Args:
            template: Template configuration
            context: Template context
            
        Returns:
            Filled LaTeX source code
            
        Raises:
            LaTeXRenderError: If template rendering fails
        """
        try:
            # Load template
            template_name = Path(template.path).name
            jinja_template = self.jinja_env.get_template(template_name)
            
            # Render with context
            latex_source = jinja_template.render(**context)
            
            return latex_source
            
        except TemplateError as e:
            raise LaTeXRenderError(f"Template rendering failed: {str(e)}")
        except Exception as e:
            raise LaTeXRenderError(f"Unexpected error during template fill: {str(e)}")
    
    def _compile_latex(
        self,
        tex_path: Path,
        engine: str = "pdflatex"
    ) -> Tuple[Path, Optional[str]]:
        """
        Compile .tex file to PDF using LaTeX engine.
        
        Args:
            tex_path: Path to .tex file
            engine: LaTeX engine (pdflatex, xelatex, lualatex)
            
        Returns:
            Tuple of (pdf_path, compilation_log)
            
        Raises:
            LaTeXRenderError: If compilation fails
        """
        # Validate engine
        valid_engines = ['pdflatex', 'xelatex', 'lualatex', 'latex']
        if engine not in valid_engines:
            logger.warning(f"Unknown engine '{engine}', defaulting to 'pdflatex'")
            engine = 'pdflatex'
        
        # Build compilation command
        # Run twice for proper reference resolution
        cmd = [
            engine,
            '-interaction=nonstopmode',  # Don't stop on errors
            '-output-directory', str(tex_path.parent),
            str(tex_path.name)
        ]
        
        compile_log = []
        
        try:
            # First pass
            logger.info(f"Compiling LaTeX (pass 1): {engine} {tex_path.name}")
            result = subprocess.run(
                cmd,
                cwd=tex_path.parent,
                capture_output=True,
                text=True,
                timeout=30
            )
            compile_log.append(f"=== Pass 1 ===\n{result.stdout}\n{result.stderr}")
            
            # Second pass for references
            logger.info(f"Compiling LaTeX (pass 2): {engine} {tex_path.name}")
            result = subprocess.run(
                cmd,
                cwd=tex_path.parent,
                capture_output=True,
                text=True,
                timeout=30
            )
            compile_log.append(f"=== Pass 2 ===\n{result.stdout}\n{result.stderr}")
            
            # Check for PDF output
            pdf_path = tex_path.with_suffix('.pdf')
            if not pdf_path.exists():
                error_log = '\n'.join(compile_log)
                raise LaTeXRenderError(
                    f"PDF compilation failed. No output file generated.\n"
                    f"Compilation log:\n{error_log}"
                )
            
            logger.info(f"Successfully compiled PDF: {pdf_path}")
            return pdf_path, '\n'.join(compile_log)
            
        except subprocess.TimeoutExpired:
            raise LaTeXRenderError("LaTeX compilation timed out (30s limit)")
        except FileNotFoundError:
            raise LaTeXRenderError(
                f"LaTeX engine '{engine}' not found. "
                "Please install a LaTeX distribution (TeX Live, MiKTeX, etc.)"
            )
        except Exception as e:
            raise LaTeXRenderError(f"Compilation error: {str(e)}")
    
    def render_from_template_string(
        self,
        resume: Resume,
        template_string: str,
        output_filename: Optional[str] = None,
        engine: str = "pdflatex"
    ) -> Tuple[str, str, Optional[str]]:
        """
        Render resume using a template string instead of file.
        
        Useful for testing or dynamic templates.
        
        Args:
            resume: Resume data
            template_string: Raw LaTeX template as string
            output_filename: Output filename (without extension)
            engine: LaTeX engine to use
            
        Returns:
            Tuple of (tex_path, pdf_path, compilation_log)
        """
        if not output_filename:
            output_filename = f"resume_{resume.full_name.replace(' ', '_').lower()}"
        
        # Build basic template config
        template = ResumeTemplate(
            id="inline",
            name="Inline Template",
            path="inline.tex",
            engine=engine,
            field_to_anchor={}
        )
        
        # Build context
        context = self._build_template_context(resume, template)
        
        # Render template string directly
        try:
            jinja_template = Template(
                template_string,
                block_start_string='\\BLOCK{',
                block_end_string='}',
                variable_start_string='\\VAR{',
                variable_end_string='}',
                autoescape=False
            )
            tex_source = jinja_template.render(**context)
        except Exception as e:
            raise LaTeXRenderError(f"Template rendering failed: {str(e)}")
        
        # Write and compile
        tex_path = self.output_dir / f"{output_filename}.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(tex_source)
        
        pdf_path, compile_log = self._compile_latex(tex_path, engine)
        
        return str(tex_path), str(pdf_path), compile_log

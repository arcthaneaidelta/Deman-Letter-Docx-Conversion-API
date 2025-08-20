from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from docxtpl import DocxTemplate, RichText
import uvicorn
import os
import io
import logging
from pathlib import Path
from typing import Optional
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Document Generation API",
    description="API for generating DOCX documents from templates",
    version="1.0.0"
)

class DocxData(BaseModel):
    date: Optional[str] = Field(None, description="Date for the document")
    defendant: Optional[str] = Field(None, description="Defendant name")
    street_address: Optional[str] = Field(None, description="Street address")
    state_address: Optional[str] = Field(None, description="State address")
    plaintiff_full_name: Optional[str] = Field(None, description="Plaintiff full name")
    pronoun: Optional[str] = Field(None, description="Pronoun")
    clauses: Optional[str] = Field(None, description="Clauses")
    mr_ms_last_name: Optional[str] = Field(None, description="Mr/Ms Last name")
    start_date: Optional[str] = Field(None, description="Start date")
    job_title: Optional[str] = Field(None, description="Job title")
    hourly_wage_annual_salary: Optional[str] = Field(None, description="Wage/Salary")
    end_date: Optional[str] = Field(None, description="End date")
    paragraphs_concerning_wrongful_termination: Optional[str] = Field(None, description="Wrongful termination paragraphs")
    paragraphs_concerning_labor_code_violations: Optional[str] = Field(None, description="Labor code violations paragraphs")
    Delete_a_or_b: Optional[str] = Field(None, description="Delete option")
    damages_formatted: Optional[str] = Field(None, description="Formatted damages")
    conclusion: Optional[str] = Field(None, description="Conclusion")
    company_name: Optional[str] = Field(None, description="Company name")
    client_name: Optional[str] = Field(None, description="Client name")

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "defendant": "ABC Corporation",
                "street_address": "123 Main St",
                "state_address": "California, 90210",
                "plaintiff_full_name": "John Doe",
                "pronoun": "he/him",
                "client_name": "John Doe",
                "company_name": "ABC Corporation"
            }
        }

def get_template_path() -> Path:
    """Get the template file path, checking multiple possible locations"""
    template_name = "template2.docx"
    
    # Check current directory first
    current_dir = Path.cwd()
    template_path = current_dir / template_name
    
    if template_path.exists():
        return template_path
    
    # Check if we're in a subdirectory, look in parent directories
    for parent in current_dir.parents:
        template_path = parent / template_name
        if template_path.exists():
            return template_path
    
    # Check common template directories
    common_paths = [
        Path("templates") / template_name,
        Path("assets") / template_name,
        Path("static") / template_name,
    ]
    
    for path in common_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(f"Template file '{template_name}' not found in any expected location")

def safe_rich_text(value: Optional[str], **kwargs) -> RichText:
    """Safely create RichText object, handling None values"""
    if value is None:
        value = ""
    
    # Set default formatting
    default_kwargs = {
        "color": "000000",
        "size": 24
    }
    default_kwargs.update(kwargs)
    
    return RichText(str(value), **default_kwargs)

def create_context(data: DocxData) -> dict:
    """Create context dictionary for template rendering"""
    context = {
        'date': safe_rich_text(data.date, bold=True, underline=True),
        'defendant': safe_rich_text(data.defendant, bold=True),
        'street_address': safe_rich_text(data.street_address, bold=True),
        'state_address': safe_rich_text(data.state_address, bold=True),
        'plaintiff_full_name': safe_rich_text(data.plaintiff_full_name, bold=True),
        'pronoun': safe_rich_text(data.pronoun),
        'clauses': safe_rich_text(data.clauses),
        'mr_ms_last_name': safe_rich_text(data.mr_ms_last_name, bold=True),
        'start_date': safe_rich_text(data.start_date, bold=True),
        'job_title': safe_rich_text(data.job_title, bold=True),
        'hourly_wage_annual_salary': safe_rich_text(data.hourly_wage_annual_salary, bold=True),
        'end_date': safe_rich_text(data.end_date, bold=True),
        'paragraphs_concerning_wrongful_termination': safe_rich_text(data.paragraphs_concerning_wrongful_termination),
        'paragraphs_concerning_labor_code_violations': safe_rich_text(data.paragraphs_concerning_labor_code_violations),
        'Delete_a_or_b': safe_rich_text(data.Delete_a_or_b),
        'damages_formatted': safe_rich_text(data.damages_formatted, bold=True),
        'conclusion': safe_rich_text(data.conclusion),
        'company_name': safe_rich_text(data.company_name, bold=True),
        'client_name': safe_rich_text(data.client_name, bold=True),
    }
    return context

@app.get("/")
def root():
    return {
        "status": "ok", 
        "message": "Document Generation API", 
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        # Check if template file exists
        template_path = get_template_path()
        return {
            "status": "healthy",
            "message": "API is running correctly",
            "template_found": True,
            "template_path": str(template_path)
        }
    except FileNotFoundError as e:
        return {
            "status": "unhealthy",
            "message": str(e),
            "template_found": False
        }

class FileStreamWrapper:
    """Wrapper to ensure proper file stream handling"""
    def __init__(self, stream: io.BytesIO):
        self.stream = stream
        self.stream.seek(0)
    
    def __iter__(self):
        return self
    
    def __next__(self):
        chunk = self.stream.read(8192)  # 8KB chunks
        if not chunk:
            raise StopIteration
        return chunk

@app.post("/generate-docx/")
async def generate_docx(data: DocxData):
    """Generate DOCX document from template and provided data"""
    try:
        logger.info("Starting document generation")
        
        # Get template path
        template_path = get_template_path()
        logger.info(f"Using template: {template_path}")
        
        # Load template
        template = DocxTemplate(str(template_path))
        
        # Create context
        context = create_context(data)
        
        # Render template
        template.render(context)
        
        # Create output stream
        output_stream = io.BytesIO()
        
        # Save to stream
        template.save(output_stream)
        output_stream.seek(0)
        
        # Create filename with timestamp to avoid caching issues
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"document_{timestamp}.docx"
        
        # Prepare headers
        headers = {
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(len(output_stream.getvalue())),
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0"
        }
        
        logger.info(f"Document generated successfully, size: {len(output_stream.getvalue())} bytes")
        
        # Return streaming response
        return StreamingResponse(
            FileStreamWrapper(output_stream),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers=headers
        )
        
    except FileNotFoundError as e:
        logger.error(f"Template file not found: {e}")
        raise HTTPException(status_code=404, detail=f"Template file not found: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error generating document: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating document: {str(e)}")

@app.get("/template-info")
def get_template_info():
    """Get information about the template file"""
    try:
        template_path = get_template_path()
        file_size = template_path.stat().st_size
        return {
            "template_path": str(template_path),
            "template_exists": True,
            "file_size_bytes": file_size,
            "file_size_kb": round(file_size / 1024, 2)
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return Response(
        content=f"Internal server error: {str(exc)}",
        status_code=500,
        media_type="text/plain"
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=port,
        reload=False,  # Disable reload in production
        access_log=True
    )

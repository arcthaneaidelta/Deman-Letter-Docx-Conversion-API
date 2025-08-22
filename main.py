from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
from docxtpl import DocxTemplate
from jinja2 import Environment, StrictUndefined
import uvicorn
import os
import uuid
import io
import tempfile
from pathlib import Path

# Define input schema
class DemandLetterData(BaseModel):
    date: str = ""
    defendant: str = ""
    street_address: str = ""
    state_address: str = ""
    plaintiff_full_name: str = ""
    pronoun: str = ""
    clauses: str = ""
    mr_ms_last_name: str = ""
    start_date: str = ""
    job_title: str = ""
    hourly_wage_annual_salary: str = ""
    end_date: str = ""
    paragraphs_concerning_wrongful_termination: str = ""
    paragraphs_concerning_labor_code_violations: str = ""
    delete_a_or_b: str = ""
    damages_formatted: str = ""
    conclusion: str = ""
    company_name: str = ""
    client_name: str = ""

app = FastAPI(title="Demand Letter Generator API", version="1.0.0")

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Demand Letter API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Additional health check endpoint"""
    return {"status": "healthy", "service": "demand-letter-generator"}

@app.post("/generate-letter")
async def generate_letter(data: DemandLetterData):
    """Generate a demand letter from template and return as downloadable file"""
    
    try:
        # Check if template exists
        template_path = Path("template.docx")
        if not template_path.exists():
            raise HTTPException(
                status_code=500, 
                detail="Template file 'template.docx' not found. Please ensure it exists in the project root."
            )
        
        # Convert input to dictionary, handling None values
        context = {}
        for key, value in data.dict().items():
            if value is None:
                context[key] = ""
            else:
                context[key] = str(value)
        
        # Load and render template
        doc = DocxTemplate(str(template_path))
        
        # Set up Jinja2 environment to be strict about undefined variables
        doc.env = Environment(undefined=StrictUndefined)
        
        # Render the document with context
        doc.render(context)
        
        # Save to memory buffer instead of file system
        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        
        # Create response with proper headers
        response = Response(
            content=buffer.getvalue(),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": "attachment; filename=demand_letter.docx",
                "Content-Type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            }
        )
        
        return response
        
    except Exception as e:
        # Log the error and return a proper HTTP error response
        print(f"Error generating letter: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate letter: {str(e)}")

# Alternative endpoint for n8n compatibility
@app.post("/generate-docx")
async def generate_docx(data: DemandLetterData):
    """Alternative endpoint name for n8n compatibility"""
    return await generate_letter(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",  # Use string format for better Railway compatibility
        host="0.0.0.0", 
        port=port,
        reload=False  # Disable reload in production
    )

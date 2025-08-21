from fastapi import FastAPI, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from docxtpl import DocxTemplate
from jinja2 import Environment, StrictUndefined
import uvicorn
import os
import uuid

# Define input schema
class DemandLetterData(BaseModel):
    date: str
    defendant: str
    street_address: str
    state_address: str
    plaintiff_full_name: str
    pronoun: str
    clauses: str
    mr_ms_last_name: str
    start_date: str
    job_title: str
    hourly_wage_annual_salary: str
    end_date: str
    paragraphs_concerning_wrongful_termination: str
    paragraphs_concerning_labor_code_violations: str
    Delete_a_or_b: str
    damages_formatted: str
    conclusion: str
    company_name: str
    client_name: str


app = FastAPI(title="Demand Letter Generator API")


@app.post("/generate-letter")
async def generate_letter(data: DemandLetterData):
    # Convert input to dictionary
    context = {k: ("" if v is None else str(v)) for k, v in data.dict().items()}

    # Load template
    template = DocxTemplate("template.docx")
    template.env = Environment(undefined=StrictUndefined)

    # Render
    template.render(context)

    # Save file with unique name
    output_filename = f"letter_{uuid.uuid4().hex}.docx"
    template.save(output_filename)

    # Return file as response
    return FileResponse(
        output_filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="demand_letter.docx"
    )


@app.get("/")
async def root():
    return {"message": "Demand Letter API is running. Use POST /generate-letter with JSON data."}


if __name__ == "__main__":
    # For local testing
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

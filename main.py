from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from docxtpl import DocxTemplate, RichText
import io

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "message": "API is healthy 🚀"}

@app.get("/")
def root():
    return {"status": "ok", "message": "This is your root Endppoint!"}

class DocxData(BaseModel):
    date: str | None = None
    defendant: str | None = None
    street_address: str | None = None
    state_address: str | None = None
    plaintiff_full_name: str | None = None
    pronoun: str | None = None
    clauses: str | None = None
    mr_ms_last_name: str | None = None
    start_date: str | None = None
    job_title: str | None = None
    hourly_wage_annual_salary: str | None = None
    end_date: str | None = None
    paragraphs_concerning_wrongful_termination: str | None = None
    paragraphs_concerning_labor_code_violations: str | None = None
    Delete_a_or_b: str | None = None
    damages_formatted: str | None = None
    conclusion: str | None = None
    company_name: str | None = None
    client_name: str | None = None


@app.post("/generate-docx/")
def generate_docx(data: DocxData):
    context = {}
    context['date'] = RichText(str(data.date), color="000000", size=24, bold=True, underline=True)
    context['defendant'] = RichText(str(data.defendant), color="000000", size=24, bold=True)
    context['street_address'] = RichText(str(data.street_address), color="000000",size=24,bold=True)
    context['state_address'] = RichText(str(data.state_address), color="000000",size=24,bold=True)
    context['plaintiff_full_name'] = RichText(str(data.plaintiff_full_name), color="000000",size=24,bold=True)
    context['pronoun'] = RichText(str(data.pronoun), color="000000",size=24)
    context['clauses'] = RichText(str(data.clauses), color="000000",size=24)
    context['mr_ms_last_name'] = RichText(str(data.mr_ms_last_name), color="000000",size=24,bold=True)
    context['start_date'] = RichText(str(data.start_date), color="000000",size=24,bold=True)
    context['job_title'] = RichText(str(data.job_title), color="000000",size=24,bold=True)
    context['hourly_wage_annual_salary'] = RichText(str(data.hourly_wage_annual_salary), color="000000",size=24,bold=True)
    context['end_date'] = RichText(str(data.end_date), color="000000",size=24,bold=True)
    context['paragraphs_concerning_wrongful_termination'] = RichText(str(data.paragraphs_concerning_wrongful_termination), color="000000",size=24)
    context['paragraphs_concerning_labor_code_violations'] = RichText(str(data.paragraphs_concerning_labor_code_violations), color="000000",size=24)
    context['Delete_a_or_b'] = RichText(str(data.Delete_a_or_b), color="000000",size=24)
    context['damages_formatted'] = RichText(str(data.damages_formatted), color="000000",size=24,bold=True)
    context['conclusion'] = RichText(str(data.conclusion), color="000000",size=24)
    context['company_name'] = RichText(str(data.company_name), color="000000",size=24,bold=True)
    context['client_name'] = RichText(str(data.client_name), color="000000",size=24,bold=True)

    template = DocxTemplate("template2.docx")
    template.render(context)

    file_stream = io.BytesIO()
    template.save(file_stream)
    file_stream.seek(0)

    headers = {
        "Content-Disposition": "attachment; filename=final_output.docx"
    }
    return StreamingResponse(
        file_stream,
        media_type=(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        headers=headers
    )



if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)))

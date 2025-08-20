
# 📝 Demand Letter API

Generate Microsoft Word (`.docx`) documents dynamically from JSON payloads using **FastAPI** + **docxtpl**.
Designed for **Railway deployment** but works locally too.

---

## 🚀 Features

* Generate `.docx` files from **Word templates** (`template2.docx`)
* Dynamic **JSON → Template Variables** replacement
* Optional **RichText styling** for variables
* **/health** endpoint for monitoring & Railway health checks
* Ready for **Docker, Railway, or local uvicorn** deployment

---

## 📂 Project Structure

```
demand-letter-api/
│── main.py              # FastAPI application
│── template2.docx       # Word template (with {{variables}})
│── requirements.txt     # Python dependencies
│── Procfile             # Railway process definition
│── README.md            # Documentation
```

---

## 📦 Installation

### 1. Clone Repository

```bash
git clone https://github.com/<your-username>/demand-letter-api.git
cd demand-letter-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## ▶ Running Locally

Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:

```
http://127.0.0.1:8000
```

Interactive API docs:

```
http://127.0.0.1:8000/docs
```

---

## 🔗 API Endpoints

### ✅ Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "ok",
  "message": "API is healthy 🚀"
}
```

---

### 📝 Generate DOCX

```http
POST /generate-docx/
Content-Type: application/json
```

**Request Example:**

```json
{
  "data": {
    "date":"March 23, 2025",
    "defendant": "Ms. Survillian",
    "company_name": "TechCorp Inc.",
    "client_name": "Jane Doe",
    "job_title": "Software Engineer",
    "damages_formatted": "$50,000"
  }
}
```

**Curl Example:**

```bash
curl -X POST "http://127.0.0.1:8000/generate-docx/" \
     -H "Content-Type: application/json" \
     -d @sample.json \
     --output result.docx
```

The response will be a downloadable **Word document** (`result.docx`).

---

## 🛠 Requirements

* Python 3.9+
* FastAPI
* uvicorn
* docxtpl
* python-docx

---

## 📜 License

MIT License – free to use and modify.


Do you want me to also **include a `sample.json` file** in the repo (so you can test `curl` directly after deploy), or just keep the README example?

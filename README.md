# FastAPI DOCX Processing API - Usage Guide

## 1. Setup & Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Installation Steps
```bash
# Create a virtual environment (recommended)
python -m venv docx_api_env
source docx_api_env/bin/activate  # On Windows: docx_api_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Alternative with uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

## 2. API Documentation

Once running, access the interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 3. Using the API Endpoints

### 3.1 POST /submit-docx - Extract Highlighted Text

**Purpose**: Extract all highlighted text from a DOCX file

#### Using curl:
```bash
curl -X POST "http://localhost:8000/submit-docx" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.docx"
```

#### Using Python requests:
```python
import requests

url = "http://localhost:8000/submit-docx"
files = {"file": open("document.docx", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

#### Expected Response:
```json
{
  "success": true,
  "filename": "document.docx",
  "highlighted_text_count": 2,
  "highlighted_texts": [
    {
      "text": "Important deadline",
      "highlight_color": "yellow",
      "paragraph_index": 0,
      "run_index": 3
    },
    {
      "text": "Critical information",
      "highlight_color": "cyan",
      "paragraph_index": 2,
      "run_index": 1
    }
  ],
  "processed_at": "2025-07-14T10:30:00.123456"
}
```

### 3.2 POST /convert-xml - Convert DOCX to XML

**Purpose**: Convert a DOCX file to XML format

#### Using curl:
```bash
curl -X POST "http://localhost:8000/convert-xml" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.docx" \
  -o "output.xml"
```

#### Using Python requests:
```python
import requests

url = "http://localhost:8000/convert-xml"
files = {"file": open("document.docx", "rb")}

response = requests.post(url, files=files)

# Save the XML response
with open("output.xml", "w", encoding="utf-8") as f:
    f.write(response.text)
```

#### Using JavaScript (fetch):
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('http://localhost:8000/convert-xml', {
    method: 'POST',
    body: formData
})
.then(response => response.text())
.then(xmlContent => {
    // Handle XML content
    console.log(xmlContent);
});
```

### 3.3 POST /convert-docx - Convert XML to DOCX

**Purpose**: Convert an XML file back to DOCX format

#### Using curl:
```bash
curl -X POST "http://localhost:8000/convert-docx" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/document.xml" \
  -o "output.docx"
```

#### Using Python requests:
```python
import requests

url = "http://localhost:8000/convert-docx"
files = {"file": open("document.xml", "rb")}

response = requests.post(url, files=files)

# Save the DOCX response
with open("output.docx", "wb") as f:
    f.write(response.content)
```

## 4. Complete Python Client Example

Here's a complete example showing how to use all endpoints:

```python
import requests
import json
from pathlib import Path

class DocxAPIClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def extract_highlighted_text(self, docx_file_path):
        """Extract highlighted text from DOCX file"""
        url = f"{self.base_url}/submit-docx"
        
        with open(docx_file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None
    
    def convert_docx_to_xml(self, docx_file_path, output_xml_path):
        """Convert DOCX to XML"""
        url = f"{self.base_url}/convert-xml"
        
        with open(docx_file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            with open(output_xml_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"XML saved to {output_xml_path}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False
    
    def convert_xml_to_docx(self, xml_file_path, output_docx_path):
        """Convert XML to DOCX"""
        url = f"{self.base_url}/convert-docx"
        
        with open(xml_file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            with open(output_docx_path, "wb") as f:
                f.write(response.content)
            print(f"DOCX saved to {output_docx_path}")
            return True
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return False

# Usage example
if __name__ == "__main__":
    client = DocxAPIClient()
    
    # Extract highlighted text
    result = client.extract_highlighted_text("sample.docx")
    if result:
        print(f"Found {result['highlighted_text_count']} highlighted texts:")
        for item in result['highlighted_texts']:
            print(f"- '{item['text']}' (Color: {item['highlight_color']})")
    
    # Convert DOCX to XML
    client.convert_docx_to_xml("sample.docx", "output.xml")
    
    # Convert XML back to DOCX
    client.convert_xml_to_docx("output.xml", "converted.docx")
```

## 5. Testing with Postman

### Setting up requests in Postman:

1. **Create a new request**
2. **Set method to POST**
3. **Enter URL**: `http://localhost:8000/submit-docx`
4. **Go to Body tab**
5. **Select form-data**
6. **Add key "file" with type "File"**
7. **Upload your DOCX file**
8. **Send request**

## 6. Health Check & Status

```bash
# Check if API is running
curl http://localhost:8000/health

# Get API information
curl http://localhost:8000/
```

## 7. Error Handling

The API returns appropriate HTTP status codes:
- **200**: Success
- **400**: Bad request (invalid file format, empty file, etc.)
- **422**: Validation error
- **500**: Internal server error

Example error response:
```json
{
  "detail": "File must be a DOCX document"
}
```

## 8. File Format Requirements

- **For /submit-docx and /convert-xml**: Files must have `.docx` extension
- **For /convert-docx**: Files must have `.xml` extension
- Files must not be empty
- DOCX files must be valid Word documents

## 9. Production Deployment

For production deployment, consider:

```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 10. Troubleshooting

### Common Issues:

1. **"Invalid DOCX file format"**
   - Ensure file is a valid .docx file
   - Check file is not corrupted

2. **"Empty file uploaded"**
   - Verify file contains data
   - Check file upload process

3. **Connection errors**
   - Ensure API server is running
   - Check port 8000 is available
   - Verify firewall settings

### Debug Mode:
Run with debug logging:
```bash
python main.py --log-level debug
```

This comprehensive guide should help you effectively use the DOCX processing API in various scenarios!

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
import xmltodict
import dicttoxml
import zipfile
import io
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import re
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="DOCX Processing API",
    description="API for processing DOCX files, extracting highlighted text, and converting between DOCX and XML formats",
    version="1.0.0"
)

# XML namespaces for DOCX processing
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

class DocxProcessor:
    """Utility class for processing DOCX files"""
    
    @staticmethod
    def extract_text_from_run(run_elem):
        """Extract text from a run element"""
        text_parts = []
        for text_elem in run_elem.findall('.//w:t', NAMESPACES):
            if text_elem.text:
                text_parts.append(text_elem.text)
        return ''.join(text_parts)
    
    @staticmethod
    def is_highlighted(run_elem):
        """Check if a run element has highlighting"""
        highlight_elem = run_elem.find('.//w:highlight', NAMESPACES)
        return highlight_elem is not None
    
    @staticmethod
    def get_highlight_color(run_elem):
        """Get the highlight color from a run element"""
        highlight_elem = run_elem.find('.//w:highlight', NAMESPACES)
        if highlight_elem is not None:
            return highlight_elem.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', 'yellow')
        return None
    
    @staticmethod
    def extract_highlighted_text(document_xml: str) -> List[Dict[str, Any]]:
        """Extract highlighted text from document XML"""
        try:
            root = ET.fromstring(document_xml)
            highlighted_texts = []
            
            # Find all paragraphs
            paragraphs = root.findall('.//w:p', NAMESPACES)
            
            for para_idx, paragraph in enumerate(paragraphs):
                # Find all runs in the paragraph
                runs = paragraph.findall('.//w:r', NAMESPACES)
                
                for run_idx, run in enumerate(runs):
                    if DocxProcessor.is_highlighted(run):
                        text = DocxProcessor.extract_text_from_run(run)
                        if text.strip():  # Only include non-empty text
                            highlight_color = DocxProcessor.get_highlight_color(run)
                            highlighted_texts.append({
                                'text': text.strip(),
                                'highlight_color': highlight_color,
                                'paragraph_index': para_idx,
                                'run_index': run_idx
                            })
            
            return highlighted_texts
            
        except ET.ParseError as e:
            logger.error(f"XML parsing error: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid XML format: {e}")
        except Exception as e:
            logger.error(f"Error extracting highlighted text: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {e}")

    @staticmethod
    def docx_to_xml(docx_content: bytes) -> str:
        """Convert DOCX to XML format"""
        try:
            with zipfile.ZipFile(io.BytesIO(docx_content), 'r') as docx_zip:
                # Read the main document XML
                document_xml = docx_zip.read('word/document.xml').decode('utf-8')
                return document_xml
        except zipfile.BadZipFile:
            raise HTTPException(status_code=400, detail="Invalid DOCX file format")
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid DOCX structure - missing document.xml")
        except Exception as e:
            logger.error(f"Error converting DOCX to XML: {e}")
            raise HTTPException(status_code=500, detail=f"Error processing DOCX file: {e}")

    @staticmethod
    def xml_to_docx(xml_content: str) -> bytes:
        """Convert XML to DOCX format"""
        try:
            # Create a minimal DOCX structure
            docx_buffer = io.BytesIO()
            
            with zipfile.ZipFile(docx_buffer, 'w', zipfile.ZIP_DEFLATED) as docx_zip:
                # Add Content_Types
                content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
    <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''
                docx_zip.writestr('[Content_Types].xml', content_types)
                
                # Add main relationships
                main_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
                docx_zip.writestr('_rels/.rels', main_rels)
                
                # Add document relationships
                doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
                docx_zip.writestr('word/_rels/document.xml.rels', doc_rels)
                
                # Add minimal styles
                styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:docDefaults>
        <w:rPrDefault>
            <w:rPr>
                <w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>
                <w:sz w:val="22"/>
                <w:szCs w:val="22"/>
                <w:lang w:val="en-US" w:eastAsia="en-US" w:bidi="ar-SA"/>
            </w:rPr>
        </w:rPrDefault>
    </w:docDefaults>
</w:styles>'''
                docx_zip.writestr('word/styles.xml', styles)
                
                # Add the main document XML
                docx_zip.writestr('word/document.xml', xml_content)
            
            docx_buffer.seek(0)
            return docx_buffer.read()
            
        except ET.ParseError as e:
            raise HTTPException(status_code=400, detail=f"Invalid XML format: {e}")
        except Exception as e:
            logger.error(f"Error converting XML to DOCX: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating DOCX file: {e}")

@app.post("/submit-docx")
async def submit_docx(file: UploadFile = File(...)):
    """
    Extract highlighted text from a DOCX file
    
    Returns:
        JSON object containing all highlighted text with metadata
    """
    # Validate file type
    if not file.filename.lower().endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    if file.content_type not in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/octet-stream']:
        logger.warning(f"Unexpected content type: {file.content_type}")
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Convert DOCX to XML
        document_xml = DocxProcessor.docx_to_xml(content)
        
        # Extract highlighted text
        highlighted_texts = DocxProcessor.extract_highlighted_text(document_xml)
        
        return {
            "success": True,
            "filename": file.filename,
            "highlighted_text_count": len(highlighted_texts),
            "highlighted_texts": highlighted_texts,
            "processed_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in submit_docx: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/convert-xml")
async def convert_xml(file: UploadFile = File(...)):
    """
    Convert DOCX file to XML format
    
    Returns:
        XML file as response
    """
    # Validate file type
    if not file.filename.lower().endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Convert DOCX to XML
        xml_content = DocxProcessor.docx_to_xml(content)
        
        # Generate filename
        base_filename = file.filename.rsplit('.', 1)[0]
        xml_filename = f"{base_filename}.xml"
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": f"attachment; filename={xml_filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in convert_xml: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/convert-docx")
async def convert_docx(file: UploadFile = File(...)):
    """
    Convert XML file to DOCX format
    
    Returns:
        DOCX file as response
    """
    # Validate file type
    if not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML document")
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Decode XML content
        xml_content = content.decode('utf-8')
        
        # Convert XML to DOCX
        docx_content = DocxProcessor.xml_to_docx(xml_content)
        
        # Generate filename
        base_filename = file.filename.rsplit('.', 1)[0]
        docx_filename = f"{base_filename}.docx"
        
        return Response(
            content=docx_content,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={docx_filename}"}
        )
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Invalid XML file encoding")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in convert_docx: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@app.post("/json-to-xml-file")
async def convert(request: Request):
    data = await request.json()
    xml = dicttoxml.dicttoxml(data, attr_type=False, custom_root='root')
    return Response(content=xml, media_type='application/xml', headers={
        "Content-Disposition": "attachment; filename=output.xml"
    })


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "DOCX Processing API",
        "version": "1.0.0",
        "endpoints": {
            "/submit-docx": "Extract highlighted text from DOCX file",
            "/convert-xml": "Convert DOCX to XML",
            "/convert-docx": "Convert XML to DOCX"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

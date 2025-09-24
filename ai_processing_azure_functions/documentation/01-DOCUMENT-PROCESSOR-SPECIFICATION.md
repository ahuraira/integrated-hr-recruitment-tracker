# Document Processor Module Specification

**Module:** `shared_code/document_processor.py`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Module Overview**

The Document Processor module is responsible for robust file handling, text extraction, and content validation for CV documents. It serves as the first stage in the CV processing pipeline, converting binary file content into structured, semantic Markdown text that can be effectively processed by AI assistants.

### **Core Responsibilities:**
- Base64 file content decoding and validation
- File type detection and format validation (PDF/DOCX only)
- Text extraction with semantic structure preservation
- Page count validation and size limits enforcement
- Error handling for corrupt or password-protected files
- Markdown conversion for optimal AI processing

## **2. Functional Requirements**

### **2.1 Input Processing**
- **Accept Base64 encoded file content** from the main function
- **Validate file size** before processing (max 5-7 pages equivalent)
- **Detect file type** automatically from content headers
- **Support file formats:** PDF and DOCX only
- **Reject unsupported formats** with descriptive error messages

### **2.2 Text Extraction**
- **PDF Processing:** Use `pymupdf4llm` library for high-quality text extraction
- **DOCX Processing:** Use `python-docx` library for structured text extraction
- **Preserve document structure:** Headers, paragraphs, lists, and formatting
- **Convert to Markdown:** Generate semantic Markdown for AI consumption
- **Handle edge cases:** Empty files, image-only documents, tables

### **2.3 Content Validation**
- **Page count validation:** Ensure document is 5-7 pages maximum
- **Text content validation:** Ensure extractable text exists
- **Quality checks:** Verify minimum text length (prevent image-only CVs)
- **Character encoding:** Handle various text encodings properly

### **2.4 Error Handling**
- **Graceful failures:** Handle corrupt files without crashing
- **Password protection:** Detect and report password-protected files
- **Memory management:** Handle large files efficiently
- **Timeout protection:** Prevent hanging on problematic files

## **3. Technical Specifications**

### **3.1 Class Structure**
```python
class DocumentProcessor:
    """
    Handles CV document parsing and text extraction with enterprise-level robustness.
    """
    
    def __init__(self):
        """Initialize processor with configuration"""
        
    def process_document(self, file_content_b64: str, file_name: str) -> dict:
        """
        Main entry point for document processing
        
        Args:
            file_content_b64 (str): Base64 encoded file content
            file_name (str): Original filename with extension
            
        Returns:
            dict: Processing result with extracted text or error details
        """
        
    def _decode_file_content(self, file_content_b64: str) -> bytes:
        """Decode Base64 content with validation"""
        
    def _detect_file_type(self, file_content: bytes, file_name: str) -> str:
        """Detect file type from content and filename"""
        
    def _validate_file_size(self, file_content: bytes) -> bool:
        """Validate file size against limits"""
        
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF using pymupdf4llm"""
        
    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX using python-docx"""
        
    def _convert_to_markdown(self, text: str, file_type: str) -> str:
        """Convert extracted text to semantic Markdown"""
        
    def _validate_page_count(self, file_content: bytes, file_type: str) -> bool:
        """Validate document page count (5-7 pages max)"""
        
    def _validate_text_quality(self, text: str) -> bool:
        """Validate extracted text quality and length"""
```

### **3.2 Return Data Structure**
```python
# Success Response
{
    "success": True,
    "extracted_text": "# John Smith\n\n## Professional Summary\n...",
    "markdown_content": "# John Smith\n\n## Professional Summary\n...",
    "metadata": {
        "file_name": "John_Smith_CV.pdf",
        "file_type": "pdf",
        "file_size_bytes": 245760,
        "page_count": 3,
        "text_length": 2450,
        "processing_time_ms": 1250,
        "extraction_method": "pymupdf4llm"
    }
}

# Error Response
{
    "success": False,
    "error_type": "UNSUPPORTED_FORMAT",
    "error_message": "File format 'txt' is not supported. Only PDF and DOCX files are allowed.",
    "metadata": {
        "file_name": "document.txt",
        "file_size_bytes": 1024,
        "attempted_extraction": False
    }
}
```

### **3.3 Configuration Parameters**
```python
# File size limits
MAX_FILE_SIZE_MB = 10  # Maximum file size in megabytes
MAX_PAGE_COUNT = 7     # Maximum pages allowed
MIN_PAGE_COUNT = 1     # Minimum pages required

# Text quality thresholds
MIN_TEXT_LENGTH = 100      # Minimum characters for valid CV
MIN_WORD_COUNT = 50        # Minimum words for valid CV

# Processing timeouts
EXTRACTION_TIMEOUT_SEC = 15  # Maximum time for text extraction

# Supported formats
SUPPORTED_FORMATS = ['pdf', 'docx']
```

## **4. Error Handling Specifications**

### **4.1 Error Categories**
```python
class DocumentProcessorError(Exception):
    """Base exception for document processing errors"""
    pass

class UnsupportedFormatError(DocumentProcessorError):
    """Raised when file format is not supported"""
    pass

class FileSizeError(DocumentProcessorError):
    """Raised when file exceeds size limits"""
    pass

class ExtractionError(DocumentProcessorError):
    """Raised when text extraction fails"""
    pass

class ValidationError(DocumentProcessorError):
    """Raised when content validation fails"""
    pass
```

### **4.2 Error Response Mapping**
| Error Type | HTTP Impact | Recovery Action |
|------------|-------------|-----------------|
| `UnsupportedFormatError` | 400 Bad Request | User must provide PDF/DOCX |
| `FileSizeError` | 413 Payload Too Large | User must reduce file size |
| `ExtractionError` | 500 Internal Error | Log for investigation |
| `ValidationError` | 422 Unprocessable | User must provide valid CV |
| `TimeoutError` | 408 Request Timeout | Retry with smaller file |

## **5. Performance Requirements**

### **5.1 Processing Targets**
- **Text Extraction Time:** < 10 seconds for 7-page documents
- **Memory Usage:** < 100MB per document processing
- **File Size Support:** Up to 10MB files
- **Concurrent Processing:** Support for multiple simultaneous requests

### **5.2 Quality Metrics**
- **Text Extraction Accuracy:** >95% for well-formatted CVs
- **Structure Preservation:** Maintain headers, lists, and sections
- **Error Recovery:** Graceful handling of 99% of problematic files

## **6. Dependencies**

### **6.1 Required Libraries**
```txt
pymupdf4llm>=0.0.5         # PDF text extraction with LLM optimization
python-docx>=0.8.11        # DOCX text extraction
python-magic>=0.4.27       # File type detection
chardet>=5.2.0             # Character encoding detection
```

### **6.2 System Dependencies**
- **Azure Functions Python 3.9+** runtime
- **Memory allocation:** Minimum 512MB for file processing
- **Temporary storage:** Access to `/tmp` for file operations

## **7. Logging Requirements**

### **7.1 Information Logging**
```python
# Processing start
logging.info(f"Starting document processing for {file_name}")

# Successful extraction
logging.info(f"Successfully extracted {len(text)} characters from {file_name}")

# File validation
logging.info(f"File validation passed: {file_name} ({file_type}, {page_count} pages)")
```

### **7.2 Error Logging**
```python
# Extraction failures
logging.error(f"Failed to extract text from {file_name}: {error_message}")

# Validation failures
logging.warning(f"File validation failed for {file_name}: {validation_error}")

# Performance issues
logging.warning(f"Slow processing detected: {file_name} took {processing_time}ms")
```

## **8. Testing Considerations**

### **8.1 Unit Test Coverage**
- File type detection accuracy
- Base64 decoding validation
- Text extraction quality
- Error handling robustness
- Performance benchmarks

### **8.2 Test File Requirements**
- Valid PDF CVs (1-7 pages)
- Valid DOCX CVs (1-7 pages)
- Corrupt PDF files
- Password-protected files
- Oversized files (>10MB)
- Image-only documents
- Empty files

## **9. Security Considerations**

### **9.1 Input Validation**
- **Base64 validation:** Verify proper encoding before decoding
- **File signature verification:** Check magic bytes for file type validation
- **Size limits enforcement:** Prevent memory exhaustion attacks
- **Content scanning:** Basic malware signature detection

### **9.2 Memory Safety**
- **Stream processing:** Handle large files without loading entirely into memory
- **Temporary file cleanup:** Ensure no residual files remain
- **Exception safety:** Proper cleanup in error conditions

## **10. Integration Points**

### **10.1 Input Integration**
- **Called by:** `function_app.py` main processing function
- **Input format:** Base64 string + filename
- **Validation requirements:** Pre-validated HTTP request data

### **10.2 Output Integration**
- **Consumed by:** `candidate_data_service.py` for AI processing
- **Output format:** Structured dictionary with text and metadata
- **Error propagation:** Structured error responses for upstream handling

---

**Next Steps:**
- Implement core DocumentProcessor class
- Add comprehensive error handling
- Integrate with Azure Functions logging
- Perform thorough testing with various CV formats
- Optimize for Azure Functions consumption plan

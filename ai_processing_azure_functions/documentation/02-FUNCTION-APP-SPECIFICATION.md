# Function App Main Entry Point Specification

**Module:** `function_app.py`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Module Overview**

The Function App module serves as the main entry point for the Azure Functions application. It handles HTTP requests from Power Automate, orchestrates the entire CV processing pipeline, and returns consolidated results. This module acts as the primary interface between the external Power Automate workflow and the internal processing modules.

### **Core Responsibilities:**
- HTTP request handling and validation
- Input parameter extraction and validation
- Processing pipeline orchestration
- Global error handling and response formatting
- Performance monitoring and logging
- HTTP status code management

## **2. Functional Requirements**

### **2.1 HTTP Request Handling**
- **Accept HTTP POST requests** from Power Automate workflows
- **Validate Content-Type:** Ensure `application/json` content type
- **Parse JSON payload** with required parameters
- **Implement request timeout** handling (30-second maximum)
- **Support CORS** if needed for web-based testing

### **2.2 Input Validation**
- **Required Parameters:**
  - `fileName` (string): Original CV filename with extension
  - `fileContent` (string): Base64 encoded file content
  - `jobTitle` (string): Target position from MPR
- **Parameter Validation:**
  - Validate Base64 encoding format
  - Check filename for supported extensions (.pdf, .docx)
  - Ensure jobTitle is non-empty string
  - Validate file size before processing

### **2.3 Pipeline Orchestration**
- **Stage 1:** Document processing and text extraction
- **Stage 2:** Candidate data extraction and PII anonymization
- **Stage 3:** Skills and experience analysis
- **Result Consolidation:** Merge all stage outputs into final JSON
- **Error Recovery:** Handle partial failures gracefully

### **2.4 Response Management**
- **Success Response (HTTP 200):** Complete candidate profile JSON
- **Client Error Response (HTTP 400):** Invalid input parameters
- **Server Error Response (HTTP 500):** Processing failures
- **Timeout Response (HTTP 408):** Processing timeout exceeded

## **3. Technical Specifications**

### **3.1 Azure Function Configuration**
```python
import azure.functions as func
import azure.functions.decorators as azure_decorators
import logging
import json
import time
from typing import Dict, Any

app = func.FunctionApp()

@app.route(route="process_cv", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def cv_processing_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Main CV processing endpoint for Power Automate integration
    
    Expected JSON payload:
    {
        "fileName": "John_Smith_CV.pdf",
        "fileContent": "base64_encoded_content...",
        "jobTitle": "Senior Software Engineer"
    }
    
    Returns:
    HTTP 200: Complete candidate profile JSON
    HTTP 400: Invalid input parameters
    HTTP 500: Processing errors
    HTTP 408: Processing timeout
    """
```

### **3.2 Main Processing Function Structure**
```python
def cv_processing_function(req: func.HttpRequest) -> func.HttpResponse:
    """Main processing function with comprehensive error handling"""
    
    # Initialize processing metadata
    processing_start_time = time.time()
    correlation_id = generate_correlation_id()
    
    try:
        # Step 1: Request validation and parsing
        request_data = validate_and_parse_request(req)
        
        # Step 2: Input parameter validation
        validated_inputs = validate_input_parameters(request_data)
        
        # Step 3: Document processing
        document_result = process_document(
            validated_inputs['fileContent'], 
            validated_inputs['fileName']
        )
        
        # Step 4: Candidate data extraction and PII handling
        candidate_result = extract_candidate_data(
            document_result['markdown_content'],
            validated_inputs['jobTitle']
        )
        
        # Step 5: Consolidate results
        final_result = consolidate_processing_results(
            document_result,
            candidate_result,
            processing_start_time,
            correlation_id
        )
        
        # Step 6: Return success response
        return create_success_response(final_result)
        
    except ValidationError as e:
        return create_error_response(400, "VALIDATION_ERROR", str(e))
    except ProcessingError as e:
        return create_error_response(500, "PROCESSING_ERROR", str(e))
    except TimeoutError as e:
        return create_error_response(408, "TIMEOUT_ERROR", str(e))
    except Exception as e:
        logging.error(f"Unexpected error in CV processing: {str(e)}")
        return create_error_response(500, "UNEXPECTED_ERROR", "An unexpected error occurred during processing")
```

### **3.3 Input Validation Functions**
```python
def validate_and_parse_request(req: func.HttpRequest) -> Dict[str, Any]:
    """
    Validate HTTP request and parse JSON payload
    
    Raises:
        ValidationError: If request format is invalid
    """
    
def validate_input_parameters(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate required input parameters
    
    Args:
        request_data: Parsed request JSON
        
    Returns:
        Dict with validated parameters
        
    Raises:
        ValidationError: If parameters are invalid
    """
    
def validate_file_content(file_content_b64: str, file_name: str) -> bool:
    """
    Validate Base64 content and file format
    
    Returns:
        True if valid, raises ValidationError if invalid
    """
```

### **3.4 Response Formatting Functions**
```python
def create_success_response(result_data: Dict[str, Any]) -> func.HttpResponse:
    """Create standardized success response"""
    
def create_error_response(status_code: int, error_type: str, error_message: str) -> func.HttpResponse:
    """Create standardized error response"""
    
def consolidate_processing_results(
    document_result: Dict[str, Any],
    candidate_result: Dict[str, Any],
    start_time: float,
    correlation_id: str
) -> Dict[str, Any]:
    """Consolidate all processing results into final JSON structure"""
```

## **4. Input/Output Specifications**

### **4.1 Expected Input JSON**
```json
{
    "fileName": "John_Smith_CV.pdf",
    "fileContent": "JVBERi0xLjQKMSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFI...",
    "jobTitle": "Senior Software Engineer"
}
```

### **4.2 Success Response (HTTP 200)**
```json
{
    "processingStatus": "Success",
    "processingMetadata": {
        "totalProcessingTimeMs": 12500,
        "fileName": "John_Smith_CV.pdf",
        "jobTitle": "Senior Software Engineer",
        "processedTimestamp": "2025-09-23T10:30:00Z",
        "correlationId": "proc_20250923_103000_abc123"
    },
    "candidateProfile": {
        "candidateName": "John Smith",
        "jobTitle": "Senior Software Engineer",
        "status": "Active",
        "candidateEmail": "john.smith@email.com",
        "candidatePhone": "+1-555-123-4567",
        "linkedInUrl": "https://linkedin.com/in/johnsmith",
        "otherProfileUrls": ["https://johnsmith.dev"],
        "currentLocation": "New York, NY",
        "currentTitle": "Senior Software Engineer",
        "currentCompany": "Tech Innovations Inc",
        "professionalHeadline": "Experienced Software Engineer with Cloud Architecture Expertise",
        "totalExperienceYears": 8,
        "relevantExperienceYears": 6,
        "highestQualification": "Master of Computer Science",
        "currentSalary": "120000 USD",
        "expectedSalary": "140000 USD",
        "availabilityStatus": "Available in 30 days",
        "visaStatus": "Permanent Resident"
    },
    "professionalAnalysis": {
        "aiConfidenceScore": 85,
        "aiRemarks": "Strong technical background with relevant industry experience",
        "overallFitScore": 78,
        "coreSkills": [
            {
                "skillName": "Project Management",
                "proficiencyLevel": "Expert",
                "yearsOfExperience": 5
            }
        ],
        "workExperience": [
            {
                "jobTitle": "Senior Software Engineer",
                "companySize": "Large Enterprise",
                "duration": "3 years 2 months",
                "keyAchievements": ["Improved system performance by 40%"]
            }
        ],
        "educationProfile": {
            "highestDegreeLevel": "Masters",
            "fieldOfStudy": "Computer Science",
            "relevantCertifications": ["AWS Certified", "PMP Certified"]
        }
    },
    "aiCallLogs": [
        {
            "stage": "candidate_data_extraction",
            "assistantId": "asst_xyz123",
            "modelUsed": "gpt-4o-mini",
            "inputTokens": 1200,
            "outputTokens": 300,
            "callDurationMs": 3500,
            "callTimestamp": "2025-09-23T10:30:01Z",
            "success": true,
            "errorDetails": null
        }
    ],
    "tokenUsageSummary": {
        "totalInputTokens": 3000,
        "totalOutputTokens": 1200,
        "totalTokens": 4200,
        "estimatedCost": "0.0042 USD"
    }
}
```

### **4.3 Error Response Examples**

#### **Validation Error (HTTP 400)**
```json
{
    "processingStatus": "Failed",
    "errorType": "VALIDATION_ERROR",
    "errorMessage": "Required parameter 'fileName' is missing",
    "processingMetadata": {
        "processedTimestamp": "2025-09-23T10:30:00Z",
        "correlationId": "proc_20250923_103000_abc123"
    },
    "validationDetails": {
        "missingParameters": ["fileName"],
        "invalidParameters": [],
        "supportedFormats": ["pdf", "docx"]
    }
}
```

#### **Processing Error (HTTP 500)**
```json
{
    "processingStatus": "Failed",
    "errorType": "PROCESSING_ERROR",
    "errorMessage": "Failed to extract text from PDF document",
    "processingMetadata": {
        "fileName": "corrupted_cv.pdf",
        "processedTimestamp": "2025-09-23T10:30:00Z",
        "correlationId": "proc_20250923_103000_abc123",
        "failedStage": "document_processing"
    },
    "debugInfo": {
        "lastSuccessfulStage": "input_validation",
        "processingTimeMs": 2500,
        "canRetry": false
    }
}
```

## **5. Error Handling Strategy**

### **5.1 Error Categories and HTTP Status Codes**
| Error Category | HTTP Status | Description | Recovery Action |
|---------------|-------------|-------------|-----------------|
| Invalid Input | 400 | Missing/invalid parameters | Fix input and retry |
| File Too Large | 413 | File exceeds size limits | Reduce file size |
| Unsupported Format | 415 | Invalid file format | Use PDF/DOCX only |
| Processing Timeout | 408 | Processing exceeded 30s | Retry with smaller file |
| AI Service Error | 502 | Azure OpenAI unavailable | Retry later |
| Internal Error | 500 | Unexpected processing error | Contact support |

### **5.2 Error Recovery Mechanisms**
```python
def handle_processing_error(error: Exception, stage: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Centralized error handling with context preservation
    
    Args:
        error: The exception that occurred
        stage: Processing stage where error occurred
        context: Processing context for debugging
        
    Returns:
        Structured error response
    """
```

### **5.3 Partial Failure Handling**
- **Document Processing Failure:** Return validation error immediately
- **Candidate Extraction Failure:** Log error, continue with empty candidate data
- **Skills Analysis Failure:** Log error, return candidate data without analysis
- **AI Service Partial Failure:** Mark failed calls in aiCallLogs, continue processing

## **6. Performance Requirements**

### **6.1 Processing Targets**
- **Total Processing Time:** < 30 seconds (hard timeout)
- **Average Processing Time:** < 15 seconds for standard CVs
- **Memory Usage:** < 512MB per request
- **Concurrent Requests:** Support up to 20 simultaneous CV processing requests

### **6.2 Monitoring Metrics**
```python
# Performance tracking
PERFORMANCE_METRICS = {
    "total_processing_time_ms": 0,
    "document_processing_time_ms": 0,
    "ai_processing_time_ms": 0,
    "response_generation_time_ms": 0,
    "memory_usage_mb": 0,
    "token_usage_total": 0
}
```

## **7. Logging and Monitoring**

### **7.1 Application Insights Integration**
```python
# Request start logging
logging.info(f"CV processing started - CorrelationId: {correlation_id}, FileName: {file_name}")

# Stage completion logging
logging.info(f"Document processing completed - CorrelationId: {correlation_id}, Duration: {duration}ms")

# Error logging
logging.error(f"Processing failed - CorrelationId: {correlation_id}, Error: {error_message}")

# Performance logging
logging.info(f"Performance metrics - CorrelationId: {correlation_id}, Metrics: {performance_metrics}")
```

### **7.2 Custom Telemetry**
- **Request volume tracking**
- **Processing time distribution**
- **Error rate monitoring**
- **Token usage tracking**
- **Success rate metrics**

## **8. Configuration Management**

### **8.1 Environment Variables**
```python
# Required environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
CV_DATA_EXTRACTOR_ASSISTANT_ID = os.getenv("CV_DATA_EXTRACTOR_ASSISTANT_ID")
CV_PII_IDENTIFIER_ASSISTANT_ID = os.getenv("CV_PII_IDENTIFIER_ASSISTANT_ID")
CV_SKILLS_ANALYST_ASSISTANT_ID = os.getenv("CV_SKILLS_ANALYST_ASSISTANT_ID")

# Optional configuration
PROCESSING_TIMEOUT_SECONDS = int(os.getenv("PROCESSING_TIMEOUT_SECONDS", "30"))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
ENABLE_DEBUG_LOGGING = os.getenv("ENABLE_DEBUG_LOGGING", "false").lower() == "true"
```

### **8.2 Configuration Validation**
```python
def validate_configuration() -> bool:
    """
    Validate all required configuration is present
    
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: If required settings are missing
    """
```

## **9. Security Considerations**

### **9.1 Input Sanitization**
- **Base64 validation:** Verify proper encoding before processing
- **File content scanning:** Basic malware signature detection
- **Size limits:** Prevent memory exhaustion attacks
- **Request rate limiting:** Prevent abuse (future consideration)

### **9.2 Sensitive Data Handling**
- **No persistent storage:** Process and discard file content immediately
- **Secure logging:** Avoid logging sensitive information
- **API key protection:** Secure environment variable access
- **CORS configuration:** Restrict to authorized origins

## **10. Testing Strategy**

### **10.1 Unit Testing**
- **Input validation testing:** Various invalid input scenarios
- **Error handling testing:** Simulate different failure modes
- **Response formatting testing:** Verify JSON structure compliance
- **Configuration testing:** Missing environment variables

### **10.2 Integration Testing**
- **End-to-end processing:** Complete CV processing workflows
- **Error propagation:** Verify error handling across modules
- **Performance testing:** Load testing with concurrent requests
- **Azure Functions runtime testing:** Deployment and execution validation

### **10.3 Test Data Requirements**
- **Valid CVs:** Various formats and content types
- **Invalid inputs:** Malformed JSON, missing parameters
- **Edge cases:** Empty files, oversized files, corrupted content
- **Performance test files:** Large documents for timeout testing

---

**Next Steps:**
- Implement main function_app.py with Azure Functions decorators
- Add comprehensive error handling and logging
- Integrate with document_processor and candidate_data_service modules
- Set up Application Insights telemetry
- Create comprehensive test suite
- Configure Azure Functions deployment settings

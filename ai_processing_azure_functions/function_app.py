"""
Azure Function App Main Entry Point
AI-Powered CV Processing Engine for TTE Recruitment Suite

This module serves as the main entry point for the Azure Functions application.
It handles HTTP requests from Power Automate, orchestrates the entire CV processing pipeline,
and returns consolidated results.

Version: 1.0
Date: September 23, 2025
"""

import azure.functions as func
import logging
import json
import time
import base64
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# Import shared modules
from shared_code.document_processor import extract_markdown_from_file, UnsupportedFileType, DocumentProcessingError
from shared_code.candidate_data_service import CandidateDataService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Function App
app = func.FunctionApp()

# Custom Exception Classes
class ValidationError(Exception):
    """Custom exception for input validation errors"""
    pass

class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

# Configuration validation
def validate_configuration() -> bool:
    """
    Validate all required configuration is present
    
    Returns:
        True if configuration is valid
        
    Raises:
        ConfigurationError: If required settings are missing
    """
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY",
        "CV_DATA_EXTRACTOR_ASSISTANT_ID",
        "CV_PII_IDENTIFIER_ASSISTANT_ID", 
        "CV_SKILLS_ANALYST_ASSISTANT_ID"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ConfigurationError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

def generate_correlation_id() -> str:
    """Generate a unique correlation ID for request tracking"""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"proc_{timestamp}_{short_uuid}"

def validate_and_parse_request(req: func.HttpRequest) -> Dict[str, Any]:
    """
    Validate HTTP request and parse JSON payload
    
    Args:
        req: Azure Functions HTTP request object
        
    Returns:
        Dict with parsed request data
        
    Raises:
        ValidationError: If request format is invalid
    """
    # Check content type
    content_type = req.headers.get('content-type', '')
    if 'application/json' not in content_type.lower():
        raise ValidationError(f"Invalid content type. Expected 'application/json', got '{content_type}'")
    
    # Parse JSON body
    try:
        request_body = req.get_body()
        if not request_body:
            raise ValidationError("Request body is empty")
        
        request_data = json.loads(request_body.decode('utf-8'))
        return request_data
    
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON format: {str(e)}")
    except Exception as e:
        raise ValidationError(f"Failed to parse request: {str(e)}")

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
    required_params = ['fileName', 'fileContent', 'jobTitle']
    missing_params = []
    
    for param in required_params:
        if param not in request_data or not request_data[param]:
            missing_params.append(param)
    
    if missing_params:
        raise ValidationError(f"Missing required parameters: {', '.join(missing_params)}")
    
    # Validate individual parameters
    file_name = request_data['fileName'].strip()
    file_content_b64 = request_data['fileContent'].strip()
    job_title = request_data['jobTitle'].strip()
    
    # Validate file name and extension
    if not file_name:
        raise ValidationError("fileName cannot be empty")
    
    file_extension = file_name.lower().split('.')[-1]
    if file_extension not in ['pdf', 'docx']:
        raise ValidationError(f"Unsupported file format '{file_extension}'. Only PDF and DOCX files are supported")
    
    # Validate Base64 content
    try:
        file_content_bytes = base64.b64decode(file_content_b64)
        if len(file_content_bytes) == 0:
            raise ValidationError("File content is empty")
        
        # Check file size (max 10MB)
        max_size_mb = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        file_size_mb = len(file_content_bytes) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise ValidationError(f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)")
            
    except Exception as e:
        if isinstance(e, ValidationError):
            raise
        raise ValidationError(f"Invalid Base64 content: {str(e)}")
    
    # Validate job title
    if not job_title:
        raise ValidationError("jobTitle cannot be empty")
    
    return {
        'fileName': file_name,
        'fileContent': file_content_bytes,
        'jobTitle': job_title
    }

def process_document(file_content: bytes, file_name: str) -> Dict[str, Any]:
    """
    Process document and extract text content
    
    Args:
        file_content: Binary file content
        file_name: Original file name
        
    Returns:
        Dict with processing results
        
    Raises:
        ProcessingError: If document processing fails
    """
    try:
        logger.info(f"Starting document processing for file: {file_name}")
        start_time = time.time()
        
        # Extract markdown content using document processor
        markdown_content = extract_markdown_from_file(file_name, file_content)
        
        processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        result = {
            'markdown_content': markdown_content,
            'file_name': file_name,
            'file_size_bytes': len(file_content),
            'extracted_text_length': len(markdown_content),
            'processing_time_ms': processing_time,
            'success': True
        }
        
        logger.info(f"Document processing completed successfully. Extracted {len(markdown_content)} characters in {processing_time:.2f}ms")
        return result
        
    except UnsupportedFileType as e:
        raise ValidationError(str(e))
    except DocumentProcessingError as e:
        raise ProcessingError(f"Document processing failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in document processing: {str(e)}")
        raise ProcessingError(f"Unexpected document processing error: {str(e)}")

def extract_candidate_data(markdown_content: str, job_title: str) -> Dict[str, Any]:
    """
    Extract candidate data and perform skills analysis using AI pipeline
    
    Args:
        markdown_content: Extracted CV text in markdown format
        job_title: Target job title from MPR
        
    Returns:
        Dict with candidate data and analysis results
    """
    try:
        logger.info("Starting candidate data extraction and analysis")
        
        # Initialize candidate data service
        candidate_service = CandidateDataService()
        
        # Run the three-stage AI pipeline
        result = candidate_service.extract_candidate_data(markdown_content, job_title)
        
        logger.info("Candidate data extraction completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error in candidate data extraction: {str(e)}")
        
        # Return fallback data structure on failure
        processing_time = 1000  # Fallback processing time
        
        fallback_result = {
            'candidateProfile': {
                'candidateName': None,
                'jobTitle': job_title,
                'status': 'Processing Failed',
                'candidateEmail': None,
                'candidatePhone': None,
                'linkedInUrl': None,
                'otherProfileUrls': [],
                'currentLocation': None,
                'currentTitle': None,
                'currentCompany': None,
                'professionalHeadline': 'Data extraction failed',
                'totalExperienceYears': None,
                'relevantExperienceYears': None,
                'highestQualification': None,
                'currentSalary': None,
                'expectedSalary': None,
                'availabilityStatus': None,
                'visaStatus': None
            },
            'professionalAnalysis': {
                'aiConfidenceScore': 0,
                'aiRemarks': 'Analysis failed due to processing error',
                'overallFitScore': 0,
                'coreSkills': [],
                'workExperience': [],
                'educationProfile': {
                    'highestDegreeLevel': None,
                    'fieldOfStudy': None,
                    'relevantCertifications': []
                }
            },
            'aiCallLogs': [
                {
                    'stage': 'processing_failed',
                    'assistantId': 'N/A',
                    'modelUsed': 'N/A',
                    'inputTokens': 0,
                    'outputTokens': 0,
                    'callDurationMs': processing_time,
                    'callTimestamp': datetime.utcnow().isoformat() + 'Z',
                    'success': False,
                    'errorDetails': str(e)
                }
            ],
            'tokenUsageSummary': {
                'totalInputTokens': 0,
                'totalOutputTokens': 0,
                'totalTokens': 0,
                'estimatedCost': '0.0000 USD'
            },
            'processing_time_ms': processing_time
        }
        
        return fallback_result

def consolidate_processing_results(
    document_result: Dict[str, Any],
    candidate_result: Dict[str, Any],
    start_time: float,
    correlation_id: str,
    original_job_title: str
) -> Dict[str, Any]:
    """
    Consolidate all processing results into final JSON structure
    
    Args:
        document_result: Results from document processing
        candidate_result: Results from candidate data extraction
        start_time: Processing start time
        correlation_id: Request correlation ID
        original_job_title: Target job title from request (position applying for)
        
    Returns:
        Dict with consolidated results
    """
    total_processing_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    
    # Use the original job title from the request (target position)
    job_title = original_job_title
    
    final_result = {
        'processingStatus': 'Success',
        'processingMetadata': {
            'totalProcessingTimeMs': int(total_processing_time),
            'fileName': document_result['file_name'],
            'jobTitle': job_title,
            'processedTimestamp': datetime.utcnow().isoformat() + 'Z',
            'correlationId': correlation_id
        },
        'candidateProfile': candidate_result.get('candidateProfile', {}),
        'professionalAnalysis': candidate_result.get('professionalAnalysis', {}),
        'aiCallLogs': candidate_result.get('aiCallLogs', []),
        'tokenUsageSummary': candidate_result.get('tokenUsageSummary', {})
    }
    
    return final_result

def create_success_response(result_data: Dict[str, Any]) -> func.HttpResponse:
    """
    Create standardized success response
    
    Args:
        result_data: Processing results
        
    Returns:
        Azure Functions HTTP response
    """
    return func.HttpResponse(
        body=json.dumps(result_data, indent=2),
        status_code=200,
        headers={'Content-Type': 'application/json'}
    )

def create_error_response(status_code: int, error_type: str, error_message: str, correlation_id: Optional[str] = None) -> func.HttpResponse:
    """
    Create standardized error response
    
    Args:
        status_code: HTTP status code
        error_type: Error category
        error_message: Error description
        correlation_id: Request correlation ID
        
    Returns:
        Azure Functions HTTP response
    """
    error_data = {
        'processingStatus': 'Failed',
        'errorType': error_type,
        'errorMessage': error_message,
        'processingMetadata': {
            'processedTimestamp': datetime.utcnow().isoformat() + 'Z'
        }
    }
    
    if correlation_id:
        error_data['processingMetadata']['correlationId'] = correlation_id
    
    # Add specific error details based on status code
    if status_code == 400:
        error_data['validationDetails'] = {
            'supportedFormats': ['pdf', 'docx'],
            'maxFileSizeMB': int(os.getenv("MAX_FILE_SIZE_MB", "10"))
        }
    elif status_code == 500:
        error_data['debugInfo'] = {
            'canRetry': True,
            'contactSupport': True
        }
    
    return func.HttpResponse(
        body=json.dumps(error_data, indent=2),
        status_code=status_code,
        headers={'Content-Type': 'application/json'}
    )

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
    
    # Initialize processing metadata
    processing_start_time = time.time()
    correlation_id = generate_correlation_id()
    
    logger.info(f"CV processing request started - CorrelationId: {correlation_id}")
    
    try:
        # Step 0: Validate configuration
        validate_configuration()
        
        # Step 1: Request validation and parsing
        logger.info(f"Validating request - CorrelationId: {correlation_id}")
        request_data = validate_and_parse_request(req)
        
        # Step 2: Input parameter validation
        logger.info(f"Validating input parameters - CorrelationId: {correlation_id}")
        validated_inputs = validate_input_parameters(request_data)
        
        # Step 3: Document processing
        logger.info(f"Starting document processing - CorrelationId: {correlation_id}")
        document_result = process_document(
            validated_inputs['fileContent'], 
            validated_inputs['fileName']
        )
        
        # Step 4: Candidate data extraction and analysis
        logger.info(f"Starting candidate data extraction - CorrelationId: {correlation_id}")
        candidate_result = extract_candidate_data(
            document_result['markdown_content'],
            validated_inputs['jobTitle']
        )
        
        # Step 5: Consolidate results
        logger.info(f"Consolidating results - CorrelationId: {correlation_id}")
        final_result = consolidate_processing_results(
            document_result,
            candidate_result,
            processing_start_time,
            correlation_id,
            validated_inputs['jobTitle']  # Pass original job title as fallback
        )
        
        # Step 6: Return success response
        total_time = (time.time() - processing_start_time) * 1000
        logger.info(f"CV processing completed successfully - CorrelationId: {correlation_id}, TotalTime: {total_time:.2f}ms")
        
        return create_success_response(final_result)
        
    except ValidationError as e:
        logger.warning(f"Validation error - CorrelationId: {correlation_id}, Error: {str(e)}")
        return create_error_response(400, "VALIDATION_ERROR", str(e), correlation_id)
        
    except ProcessingError as e:
        logger.error(f"Processing error - CorrelationId: {correlation_id}, Error: {str(e)}")
        return create_error_response(500, "PROCESSING_ERROR", str(e), correlation_id)
        
    except ConfigurationError as e:
        logger.error(f"Configuration error - CorrelationId: {correlation_id}, Error: {str(e)}")
        return create_error_response(500, "CONFIGURATION_ERROR", str(e), correlation_id)
        
    except Exception as e:
        logger.error(f"Unexpected error in CV processing - CorrelationId: {correlation_id}, Error: {str(e)}")
        return create_error_response(500, "UNEXPECTED_ERROR", "An unexpected error occurred during processing", correlation_id)

# Health check endpoint
@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint for monitoring
    
    Returns:
    HTTP 200: Service is healthy
    HTTP 500: Service configuration issues
    """
    try:
        # Basic configuration check
        validate_configuration()
        
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'version': '1.0',
            'service': 'CV Processing Engine'
        }
        
        return func.HttpResponse(
            body=json.dumps(health_data),
            status_code=200,
            headers={'Content-Type': 'application/json'}
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        error_data = {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return func.HttpResponse(
            body=json.dumps(error_data),
            status_code=500,
            headers={'Content-Type': 'application/json'}
        )

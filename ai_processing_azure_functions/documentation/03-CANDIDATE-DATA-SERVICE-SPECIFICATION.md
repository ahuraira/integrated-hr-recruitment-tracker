# Candidate Data Service Module Specification

**Module:** `shared_code/candidate_data_service.py`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Module Overview**

The Candidate Data Service module is the core orchestration engine for AI-powered CV analysis. It coordinates the three-stage processing pipeline: candidate data extraction, PII identification and anonymization, and professional skills analysis. This module implements the "Privacy by Design" approach by separating personal information handling from professional analysis.

### **Core Responsibilities:**
- **Stage 1:** Candidate data extraction using hybrid RegEx + AI approach
- **Stage 2:** PII identification and programmatic anonymization
- **Stage 3:** Professional skills and experience analysis on anonymized content
- **Integration:** Coordinate with OpenAI Service and AI Call Logger
- **Data Consolidation:** Merge all stage results into final structured output

## **2. Functional Requirements**

### **2.1 Stage 1: Candidate Data Extraction**
- **LLM-Based Extraction:** Use `CV-Data-Extractor` assistant for complete candidate information extraction
- **Single AI Call:** Extract all 18 mandatory fields in one comprehensive AI assistant call
- **Structured Output:** Enforce JSON schema compliance for consistent data format
- **Required Data Extraction:** All 18 mandatory fields from Genesis document
- **Quality Validation:** Ensure extracted data meets business requirements
- **Error Handling:** Graceful degradation when specific fields cannot be extracted

### **2.2 Stage 2: PII Identification and Anonymization**
- **PII Detection:** Use `CV-PII-Identifier` assistant to identify personal information
- **Programmatic Anonymization:** Replace identified PII with deterministic placeholders
- **Anti-Hallucination Design:** AI only identifies, Python performs replacement
- **Mapping Creation:** Maintain redaction mapping for audit and debugging
- **Quality Assurance:** Validate complete PII removal from anonymized text

### **2.3 Stage 3: Professional Skills Analysis**
- **Anonymized Processing:** Analyze professional content without personal identifiers
- **Skills Extraction:** Identify core skills with proficiency levels and experience years
- **Experience Analysis:** Structure work history with achievements and responsibilities
- **Fit Assessment:** Calculate overall fit score for target job title
- **Education Profiling:** Extract and structure educational background

### **2.4 Result Consolidation**
- **Data Integration:** Merge outputs from all three stages
- **Format Standardization:** Ensure consistent data types and structures
- **Metadata Collection:** Gather processing metrics and timing information
- **Error Aggregation:** Consolidate any stage-specific errors or warnings

## **3. Technical Specifications**

### **3.1 Class Structure**
```python
class CandidateDataService:
    """
    Orchestrates the three-stage AI processing pipeline for CV analysis
    with integrated PII anonymization capabilities.
    """
    
    def __init__(self, openai_service, ai_logger):
        """
        Initialize service with dependencies
        
        Args:
            openai_service: OpenAI service for AI assistant calls
            ai_logger: AI call logger for comprehensive logging
        """
        self.openai_service = openai_service
        self.ai_logger = ai_logger
        
    def process_candidate_cv(self, cv_text: str, job_title: str) -> dict:
        """
        Main entry point for complete CV processing pipeline
        
        Args:
            cv_text (str): Extracted CV text in Markdown format
            job_title (str): Target position from MPR
            
        Returns:
            dict: Complete candidate analysis with all three stages
        """
        
    # Stage 1: Candidate Data Extraction
    def extract_candidate_data(self, cv_text: str, job_title: str) -> dict:
        """Execute Stage 1: LLM-based candidate data extraction"""
        
    def _extract_candidate_data_ai(self, cv_text: str, job_title: str) -> dict:
        """Extract all candidate data using CV-Data-Extractor assistant"""
        
    def _validate_extracted_data(self, candidate_data: dict) -> dict:
        """Validate and clean extracted candidate data"""
        
    # Stage 2: PII Identification and Anonymization
    def identify_and_anonymize_pii(self, cv_text: str) -> dict:
        """Execute Stage 2: PII identification and programmatic anonymization"""
        
    def _identify_pii_entities(self, cv_text: str) -> dict:
        """Call CV-PII-Identifier assistant to identify PII entities"""
        
    def _generate_deterministic_placeholders(self, pii_entities: list) -> dict:
        """Generate consistent placeholders for PII types"""
        
    def _perform_text_anonymization(self, cv_text: str, pii_entities: list, placeholders: dict) -> str:
        """Replace PII with placeholders using exact string matching"""
        
    def _create_redaction_mapping(self, pii_entities: list, placeholders: dict) -> dict:
        """Create mapping of original PII to placeholders for audit trail"""
        
    def _validate_pii_removal(self, original_text: str, anonymized_text: str, pii_entities: list) -> bool:
        """Validate that all identified PII has been successfully removed"""
        
    # Stage 3: Professional Skills Analysis
    def analyze_skills_experience(self, anonymized_text: str, job_title: str) -> dict:
        """Execute Stage 3: Professional skills and experience analysis"""
        
    def _call_skills_analyst(self, anonymized_text: str, job_title: str) -> dict:
        """Call CV-Skills-Analyst assistant for professional analysis"""
        
    # Utility Methods
    def _validate_candidate_data(self, candidate_data: dict) -> bool:
        """Validate extracted candidate data completeness and quality"""
        
    def _consolidate_processing_results(self, stage1_result: dict, stage2_result: dict, stage3_result: dict) -> dict:
        """Consolidate all stage results into final output structure"""
```

### **3.2 LLM-Based Data Extraction Configuration**
```python
# CV-Data-Extractor Assistant Configuration
CANDIDATE_EXTRACTION_CONFIG = {
    "model": "gpt-4o-mini",
    "temperature": 0.1,  # Low temperature for consistent extraction
    "max_tokens": 2000,
    "timeout_seconds": 30
}

# Data validation rules
DATA_VALIDATION_RULES = {
    "email_format": r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',
    "phone_format": r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$',
    "url_format": r'^https?://[^\s/$.?#].[^\s]*$',
    "experience_range": (0, 50),  # Valid years of experience
    "salary_range": (10000, 10000000)  # Valid salary range
}

# Required candidate fields (18 total)
REQUIRED_CANDIDATE_FIELDS = [
    "candidateName", "jobTitle", "status", "candidateEmail", "candidatePhone",
    "linkedInUrl", "otherProfileUrls", "currentLocation", "currentTitle",
    "currentCompany", "professionalHeadline", "totalExperienceYears",
    "relevantExperienceYears", "highestQualification", "currentSalary",
    "expectedSalary", "availabilityStatus", "visaStatus"
]

PII_TYPES = [
    "name", "address", "organization", "school", "job_title",
    "certification_number", "license_number", "national_id"
]
```

### **3.3 PII Anonymization Implementation**
```python
class PIIAnonymizer:
    """Handles deterministic PII anonymization with audit trail"""
    
    def __init__(self):
        self.placeholder_counters = {
            "name": 0, "organization": 0, "school": 0, 
            "address": 0, "job_title": 0, "certification_number": 0,
            "license_number": 0, "national_id": 0
        }
        
    def generate_placeholder(self, pii_type: str) -> str:
        """Generate deterministic placeholder for PII type"""
        self.placeholder_counters[pii_type] += 1
        
        placeholder_templates = {
            "name": "[CANDIDATE_NAME]" if self.placeholder_counters[pii_type] == 1 else f"[PERSON_{self.placeholder_counters[pii_type]}]",
            "organization": f"[COMPANY_{self.placeholder_counters[pii_type]}]",
            "school": f"[UNIVERSITY_{self.placeholder_counters[pii_type]}]",
            "address": f"[ADDRESS_{self.placeholder_counters[pii_type]}]",
            "job_title": f"[JOB_TITLE_{self.placeholder_counters[pii_type]}]",
            "certification_number": f"[CERT_NUMBER_{self.placeholder_counters[pii_type]}]",
            "license_number": f"[LICENSE_NUMBER_{self.placeholder_counters[pii_type]}]",
            "national_id": f"[NATIONAL_ID_{self.placeholder_counters[pii_type]}]"
        }
        
        return placeholder_templates.get(pii_type, f"[{pii_type.upper()}_{self.placeholder_counters[pii_type]}]")
    
    def anonymize_text(self, text: str, pii_entities: list) -> tuple:
        """
        Perform text anonymization with exact string replacement
        
        Returns:
            tuple: (anonymized_text, redaction_mapping, replacement_log)
        """
```

### **3.4 AI Assistant Integration Points**
```python
# CV-Data-Extractor Assistant Call
CANDIDATE_EXTRACTION_PROMPT = """
Extract structured candidate information from the following CV text.
Focus on factual data extraction without inference.

Target Job Title: {job_title}

CV Text:
{cv_text}

Extract all available information according to the specified JSON schema.
Return null for any field not explicitly found in the CV.
"""

# CV-PII-Identifier Assistant Call  
PII_IDENTIFICATION_PROMPT = """
Identify all Personally Identifiable Information (PII) in the following CV text.
Focus on exact substring identification for programmatic replacement.

CV Text:
{cv_text}

Identify PII entities according to the specified JSON schema.
Provide exact substrings as they appear in the text.
Include all variations and context information.
"""

# CV-Skills-Analyst Assistant Call
SKILLS_ANALYSIS_PROMPT = """
Analyze the professional skills and experience from the anonymized CV text.
Focus on professional qualifications, skills, and experience analysis.

Target Job Title: {job_title}

Anonymized CV Text:
{anonymized_cv_text}

Provide comprehensive professional analysis according to the specified JSON schema.
Calculate fit scores and confidence levels based on the content.
"""
```

## **4. Stage Processing Specifications**

### **4.1 Stage 1: LLM-Based Candidate Data Extraction**

#### **Complete AI Extraction Process**
```python
def extract_candidate_data(self, cv_text: str, job_title: str) -> dict:
    """
    Execute Stage 1: Complete LLM-based candidate data extraction
    
    Args:
        cv_text: CV content in Markdown format
        job_title: Target position for context
        
    Returns:
        dict: Complete candidate profile with all 18 fields
    """
    try:
        # Call AI assistant for complete data extraction
        candidate_data = self._extract_candidate_data_ai(cv_text, job_title)
        
        # Validate and clean extracted data
        validation_result = self._validate_extracted_data(candidate_data)
        
        # Add processing metadata
        extraction_result = {
            "candidateProfile": candidate_data,
            "extractionMetadata": {
                "extraction_method": "llm_only",
                "validation_score": validation_result["completeness_score"],
                "quality_issues": validation_result.get("quality_issues", []),
                "extraction_timestamp": time.time()
            }
        }
        
        return extraction_result
        
    except Exception as e:
        logging.error(f"Candidate data extraction failed: {str(e)}")
        raise ExtractionError(f"Failed to extract candidate data: {str(e)}")

def _extract_candidate_data_ai(self, cv_text: str, job_title: str) -> dict:
    """
    Use AI assistant to extract all candidate information in one call
    
    Returns:
        dict: AI-extracted candidate data with all 18 fields
    """
    try:
        # Prepare comprehensive extraction prompt
        prompt = CANDIDATE_EXTRACTION_PROMPT.format(
            job_title=job_title,
            cv_text=cv_text
        )
        
        # Call CV-Data-Extractor assistant
        ai_response = self.openai_service.call_assistant(
            assistant_id=os.getenv("CV_DATA_EXTRACTOR_ASSISTANT_ID"),
            prompt=prompt,
            expected_json_schema="candidate_profile_schema"
        )
        
        # Log the AI call
        self.ai_logger.log_ai_call(
            stage="candidate_data_extraction",
            assistant_id=os.getenv("CV_DATA_EXTRACTOR_ASSISTANT_ID"),
            input_prompt=prompt,
            response=ai_response
        )
        
        # Extract candidate profile from response
        candidate_profile = ai_response.get("candidateProfile", {})
        
        # Ensure all required fields are present (set null if missing)
        for field in REQUIRED_CANDIDATE_FIELDS:
            if field not in candidate_profile:
                candidate_profile[field] = None
        
        return candidate_profile
        
    except Exception as e:
        self.ai_logger.log_ai_call_error(
            stage="candidate_data_extraction", 
            error=str(e)
        )
        # Return empty profile with error indication
        return {field: None for field in REQUIRED_CANDIDATE_FIELDS}
```

#### **Data Validation and Cleaning**
```python
def _validate_extracted_data(self, candidate_data: dict) -> dict:
    """
    Validate and clean extracted candidate data
    
    Args:
        candidate_data: Raw AI-extracted data
        
    Returns:
        dict: Validation results and cleaned data
    """
    validation_results = {
        "is_valid": True,
        "completeness_score": 0,
        "quality_issues": [],
        "missing_critical_fields": [],
        "data_quality_warnings": [],
        "cleaned_data": candidate_data.copy()
    }
    
    # Critical fields validation
    critical_fields = ["candidateName", "candidateEmail"]
    missing_critical = [field for field in critical_fields if not candidate_data.get(field)]
    
    if missing_critical:
        validation_results["is_valid"] = False
        validation_results["missing_critical_fields"] = missing_critical
    
    # Completeness score calculation
    filled_fields = sum(1 for field in REQUIRED_CANDIDATE_FIELDS if candidate_data.get(field))
    validation_results["completeness_score"] = (filled_fields / len(REQUIRED_CANDIDATE_FIELDS)) * 100
    
    # Data format validation and cleaning
    cleaned_data = validation_results["cleaned_data"]
    
    # Email validation and cleaning
    if candidate_data.get("candidateEmail"):
        email = candidate_data["candidateEmail"].strip().lower()
        if re.match(DATA_VALIDATION_RULES["email_format"], email):
            cleaned_data["candidateEmail"] = email
        else:
            validation_results["data_quality_warnings"].append("Invalid email format")
            cleaned_data["candidateEmail"] = None
    
    # Phone number cleaning
    if candidate_data.get("candidatePhone"):
        phone = re.sub(r'[^\d\+\-\(\)\s]', '', candidate_data["candidatePhone"])
        cleaned_data["candidatePhone"] = phone.strip()
    
    # URL validation
    for url_field in ["linkedInUrl", "otherProfileUrls"]:
        if candidate_data.get(url_field):
            if url_field == "otherProfileUrls" and isinstance(candidate_data[url_field], list):
                valid_urls = []
                for url in candidate_data[url_field]:
                    if re.match(DATA_VALIDATION_RULES["url_format"], url):
                        valid_urls.append(url)
                cleaned_data[url_field] = valid_urls
            elif url_field == "linkedInUrl":
                url = candidate_data[url_field]
                if not re.match(DATA_VALIDATION_RULES["url_format"], url):
                    validation_results["data_quality_warnings"].append("Invalid LinkedIn URL format")
                    cleaned_data[url_field] = None
    
    # Numeric field validation
    for field in ["totalExperienceYears", "relevantExperienceYears"]:
        if candidate_data.get(field) is not None:
            try:
                years = int(candidate_data[field])
                if DATA_VALIDATION_RULES["experience_range"][0] <= years <= DATA_VALIDATION_RULES["experience_range"][1]:
                    cleaned_data[field] = years
                else:
                    validation_results["data_quality_warnings"].append(f"Invalid {field} value: {years}")
                    cleaned_data[field] = None
            except (ValueError, TypeError):
                validation_results["data_quality_warnings"].append(f"Non-numeric {field}")
                cleaned_data[field] = None
    
    # Salary cleaning (remove currency symbols, convert to numeric if possible)
    for salary_field in ["currentSalary", "expectedSalary"]:
        if candidate_data.get(salary_field):
            salary_str = str(candidate_data[salary_field])
            # Extract numeric part and currency
            numeric_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', salary_str)
            currency_match = re.search(r'(USD|AED|EUR|GBP|\$|€|£)', salary_str, re.IGNORECASE)
            
            if numeric_match:
                numeric_value = numeric_match.group(1).replace(',', '')
                currency = currency_match.group(1) if currency_match else "USD"
                cleaned_data[salary_field] = f"{numeric_value} {currency.upper()}"
            else:
                cleaned_data[salary_field] = salary_str  # Keep original if no numeric found
    
    return validation_results
```

### **4.2 Stage 2: PII Identification and Anonymization**

#### **PII Identification Process**
```python
def _identify_pii_entities(self, cv_text: str) -> dict:
    """
    Call CV-PII-Identifier assistant to identify PII entities
    
    Returns:
        dict: PII entities with metadata
    """
    try:
        prompt = PII_IDENTIFICATION_PROMPT.format(cv_text=cv_text)
        
        # Call CV-PII-Identifier assistant
        ai_response = self.openai_service.call_assistant(
            assistant_id=os.getenv("CV_PII_IDENTIFIER_ASSISTANT_ID"),
            prompt=prompt,
            expected_json_schema="pii_entities_schema"
        )
        
        # Log the AI call
        self.ai_logger.log_ai_call(
            stage="pii_identification",
            assistant_id=os.getenv("CV_PII_IDENTIFIER_ASSISTANT_ID"),
            input_prompt=prompt,
            response=ai_response
        )
        
        return ai_response
        
    except Exception as e:
        self.ai_logger.log_ai_call_error(
            stage="pii_identification",
            error=str(e)
        )
        return {"pii_entities": []}
```

#### **Programmatic Anonymization**
```python
def _perform_text_anonymization(self, cv_text: str, pii_entities: list, placeholders: dict) -> str:
    """
    Replace PII with placeholders using exact string matching
    
    Args:
        cv_text: Original CV text
        pii_entities: List of identified PII entities
        placeholders: Generated placeholder mapping
        
    Returns:
        str: Anonymized CV text
    """
    anonymized_text = cv_text
    replacement_log = []
    
    # Sort entities by length (longest first) to prevent partial replacements
    sorted_entities = sorted(pii_entities, key=lambda x: len(x["original_value"]), reverse=True)
    
    for entity in sorted_entities:
        original_value = entity["original_value"]
        pii_type = entity["pii_type"]
        
        if original_value in anonymized_text:
            placeholder = placeholders[f"{pii_type}_{original_value}"]
            
            # Count occurrences before replacement
            occurrence_count = anonymized_text.count(original_value)
            
            # Perform exact string replacement
            anonymized_text = anonymized_text.replace(original_value, placeholder)
            
            # Log replacement
            replacement_log.append({
                "original": original_value,
                "placeholder": placeholder,
                "pii_type": pii_type,
                "occurrences_replaced": occurrence_count
            })
    
    return anonymized_text, replacement_log
```

### **4.3 Stage 3: Professional Skills Analysis**

#### **Skills Analysis Process**
```python
def analyze_skills_experience(self, anonymized_text: str, job_title: str) -> dict:
    """
    Execute Stage 3: Professional skills and experience analysis
    
    Args:
        anonymized_text: PII-free CV content
        job_title: Target position for fit analysis
        
    Returns:
        dict: Professional analysis results
    """
    try:
        prompt = SKILLS_ANALYSIS_PROMPT.format(
            job_title=job_title,
            anonymized_cv_text=anonymized_text
        )
        
        # Call CV-Skills-Analyst assistant
        ai_response = self.openai_service.call_assistant(
            assistant_id=os.getenv("CV_SKILLS_ANALYST_ASSISTANT_ID"),
            prompt=prompt,
            expected_json_schema="skills_analysis_schema"
        )
        
        # Log the AI call
        self.ai_logger.log_ai_call(
            stage="skills_analysis",
            assistant_id=os.getenv("CV_SKILLS_ANALYST_ASSISTANT_ID"),
            input_prompt=prompt,
            response=ai_response
        )
        
        return {
            "analysisMetrics": ai_response.get("analysisMetrics", {}),
            "professionalProfile": ai_response.get("professionalProfile", {})
        }
        
    except Exception as e:
        self.ai_logger.log_ai_call_error(
            stage="skills_analysis",
            error=str(e)
        )
        return {
            "analysisMetrics": {"aiConfidenceScore": 0, "aiRemarks": "Analysis failed", "overallFitScore": 0},
            "professionalProfile": {}
        }
```

## **5. Data Validation and Quality Assurance**

### **5.1 Candidate Data Validation**
```python
def _validate_candidate_data(self, candidate_data: dict) -> dict:
    """
    Validate extracted candidate data completeness and quality
    
    Returns:
        dict: Validation results with quality metrics
    """
    validation_results = {
        "is_valid": True,
        "completeness_score": 0,
        "quality_issues": [],
        "missing_critical_fields": [],
        "data_quality_warnings": []
    }
    
    # Critical fields that must be present
    critical_fields = ["candidateName", "candidateEmail", "candidatePhone"]
    missing_critical = [field for field in critical_fields if not candidate_data.get(field)]
    
    if missing_critical:
        validation_results["is_valid"] = False
        validation_results["missing_critical_fields"] = missing_critical
    
    # Calculate completeness score (18 total fields)
    total_fields = 18
    filled_fields = sum(1 for field in REQUIRED_CANDIDATE_FIELDS if candidate_data.get(field))
    validation_results["completeness_score"] = (filled_fields / total_fields) * 100
    
    # Quality checks
    if candidate_data.get("candidateEmail") and not re.match(REGEX_PATTERNS["email"], candidate_data["candidateEmail"]):
        validation_results["data_quality_warnings"].append("Email format appears invalid")
    
    if candidate_data.get("totalExperienceYears") and not isinstance(candidate_data["totalExperienceYears"], (int, float)):
        validation_results["data_quality_warnings"].append("Experience years is not numeric")
    
    return validation_results
```

### **5.2 PII Removal Validation**
```python
def _validate_pii_removal(self, original_text: str, anonymized_text: str, pii_entities: list) -> dict:
    """
    Validate that all identified PII has been successfully removed
    
    Returns:
        dict: Validation results with any remaining PII
    """
    validation_results = {
        "pii_completely_removed": True,
        "remaining_pii_entities": [],
        "anonymization_quality_score": 100
    }
    
    remaining_pii = []
    
    for entity in pii_entities:
        original_value = entity["original_value"]
        
        # Check if original PII still exists in anonymized text
        if original_value in anonymized_text:
            remaining_pii.append({
                "pii_value": original_value,
                "pii_type": entity["pii_type"],
                "occurrences": anonymized_text.count(original_value)
            })
    
    if remaining_pii:
        validation_results["pii_completely_removed"] = False
        validation_results["remaining_pii_entities"] = remaining_pii
        validation_results["anonymization_quality_score"] = max(0, 100 - (len(remaining_pii) * 20))
    
    return validation_results
```

## **6. Error Handling and Recovery**

### **6.1 Stage-Specific Error Handling**
```python
class CandidateDataServiceError(Exception):
    """Base exception for candidate data service errors"""
    pass

class ExtractionError(CandidateDataServiceError):
    """Raised when candidate data extraction fails"""
    pass

class PIIProcessingError(CandidateDataServiceError):
    """Raised when PII processing fails"""
    pass

class SkillsAnalysisError(CandidateDataServiceError):
    """Raised when skills analysis fails"""
    pass

def handle_stage_error(self, stage: str, error: Exception, context: dict) -> dict:
    """
    Handle errors at any processing stage
    
    Args:
        stage: Processing stage where error occurred
        error: The exception that occurred
        context: Additional context for debugging
        
    Returns:
        dict: Error recovery result
    """
    error_response = {
        "stage": stage,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "recovery_action": "partial_processing",
        "can_continue": False
    }
    
    # Stage-specific recovery strategies
    if stage == "candidate_data_extraction":
        # Continue with empty candidate data
        error_response["can_continue"] = True
        error_response["recovery_data"] = self._get_empty_candidate_profile()
        
    elif stage == "pii_identification":
        # Continue without anonymization (process original text)
        error_response["can_continue"] = True
        error_response["recovery_data"] = {"anonymized_text": context.get("original_text", "")}
        
    elif stage == "skills_analysis":
        # Continue with empty professional analysis
        error_response["can_continue"] = True
        error_response["recovery_data"] = self._get_empty_professional_analysis()
    
    return error_response
```

### **6.2 Partial Processing Strategy**
```python
def process_candidate_cv_with_recovery(self, cv_text: str, job_title: str) -> dict:
    """
    Process CV with comprehensive error recovery
    
    Returns:
        dict: Processing results with error handling
    """
    processing_results = {
        "candidateProfile": {},
        "professionalAnalysis": {},
        "processingErrors": [],
        "partialProcessing": False
    }
    
    # Stage 1: Candidate Data Extraction
    try:
        stage1_result = self.extract_candidate_data(cv_text, job_title)
        processing_results["candidateProfile"] = stage1_result
    except Exception as e:
        error_info = self.handle_stage_error("candidate_data_extraction", e, {"cv_text": cv_text})
        processing_results["processingErrors"].append(error_info)
        processing_results["partialProcessing"] = True
        
        if error_info["can_continue"]:
            processing_results["candidateProfile"] = error_info["recovery_data"]
    
    # Stage 2: PII Identification and Anonymization
    try:
        stage2_result = self.identify_and_anonymize_pii(cv_text)
        anonymized_text = stage2_result["anonymized_text"]
    except Exception as e:
        error_info = self.handle_stage_error("pii_identification", e, {"original_text": cv_text})
        processing_results["processingErrors"].append(error_info)
        processing_results["partialProcessing"] = True
        
        # Use original text if anonymization fails
        anonymized_text = cv_text
    
    # Stage 3: Skills Analysis
    try:
        stage3_result = self.analyze_skills_experience(anonymized_text, job_title)
        processing_results["professionalAnalysis"] = stage3_result
    except Exception as e:
        error_info = self.handle_stage_error("skills_analysis", e, {"anonymized_text": anonymized_text})
        processing_results["processingErrors"].append(error_info)
        processing_results["partialProcessing"] = True
        
        if error_info["can_continue"]:
            processing_results["professionalAnalysis"] = error_info["recovery_data"]
    
    return processing_results
```

## **7. Performance Optimization**

### **7.1 Caching Strategy**
```python
class ProcessingCache:
    """Simple in-memory cache for processing optimization"""
    
    def __init__(self):
        self.extraction_cache = {}
        self.pii_pattern_cache = {}
        
    def get_extraction_result(self, text_hash: str) -> dict:
        """Get cached extraction results"""
        return self.extraction_cache.get(text_hash)
    
    def cache_extraction_result(self, text_hash: str, result: dict):
        """Cache extraction results"""
        if len(self.extraction_cache) < 100:  # Limit cache size
            self.extraction_cache[text_hash] = result
```

### **7.2 Performance Monitoring**
```python
def _track_stage_performance(self, stage: str, start_time: float, end_time: float, metadata: dict):
    """Track performance metrics for each processing stage"""
    duration_ms = (end_time - start_time) * 1000
    
    performance_log = {
        "stage": stage,
        "duration_ms": duration_ms,
        "timestamp": time.time(),
        "metadata": metadata
    }
    
    # Log performance metrics
    self.ai_logger.log_performance_metrics(performance_log)
    
    # Alert on slow processing
    if duration_ms > 10000:  # 10 seconds
        logging.warning(f"Slow processing detected in {stage}: {duration_ms}ms")
```

## **8. Configuration and Constants**

### **8.1 Required Configuration**
```python
# Required environment variables
REQUIRED_CONFIG = {
    "CV_DATA_EXTRACTOR_ASSISTANT_ID": "Assistant ID for candidate data extraction",
    "CV_PII_IDENTIFIER_ASSISTANT_ID": "Assistant ID for PII identification", 
    "CV_SKILLS_ANALYST_ASSISTANT_ID": "Assistant ID for skills analysis",
    "AZURE_OPENAI_ENDPOINT": "Azure OpenAI service endpoint",
    "AZURE_OPENAI_API_KEY": "Azure OpenAI API key"
}

# Processing configuration
PROCESSING_CONFIG = {
    "max_retry_attempts": 3,
    "ai_call_timeout_seconds": 30,
    "max_pii_entities": 50,
    "min_anonymized_text_length": 100
}
```

### **8.2 Data Field Mappings**
```python
REQUIRED_CANDIDATE_FIELDS = [
    "candidateName", "jobTitle", "status", "candidateEmail", "candidatePhone",
    "linkedInUrl", "otherProfileUrls", "currentLocation", "currentTitle",
    "currentCompany", "professionalHeadline", "totalExperienceYears",
    "relevantExperienceYears", "highestQualification", "currentSalary",
    "expectedSalary", "availabilityStatus", "visaStatus"
]

PII_TYPES = [
    "name", "address", "organization", "school", "job_title",
    "certification_number", "license_number", "national_id"
]
```

## **9. Integration Requirements**

### **9.1 OpenAI Service Integration**
- **Dependency:** Requires initialized `OpenAIService` instance
- **Assistant IDs:** Must be configured for all three assistants
- **Error Handling:** Must handle API timeouts and rate limits
- **Response Validation:** Validate JSON schema compliance

### **9.2 AI Call Logger Integration**
- **Comprehensive Logging:** Log all AI interactions with full context
- **Performance Tracking:** Track timing and token usage
- **Error Documentation:** Log all failures with recovery actions
- **Audit Trail:** Maintain processing history for debugging

### **9.3 Function App Integration**
- **Input:** Processed CV text from document processor
- **Output:** Complete candidate analysis for final response
- **Error Propagation:** Return structured errors for HTTP response handling
- **Performance Metrics:** Provide timing data for overall performance tracking

---

**Next Steps:**
- Implement CandidateDataService class with all three stages
- Create comprehensive regex pattern library
- Integrate PII anonymization with deterministic placeholders
- Add robust error handling and recovery mechanisms
- Implement performance monitoring and caching
- Create comprehensive unit tests for all processing stages

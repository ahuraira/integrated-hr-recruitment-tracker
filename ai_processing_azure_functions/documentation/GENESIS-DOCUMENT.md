### **Project Genesis: AI-Powered CV Processing Engine for the TTE Recruitment Suite**

**Document Version:** 1.0  
**Date:** September 12, 2025  
**Project Lead:** Abu Huraira

### **1. Executive Summary & Vision**

This document outlines the functional and technical requirements for a new, intelligent automation module for our internal recruitment tracking system. The overall vision is to transform our current recruitment process into a strategic **Talent Intelligence Platform**.

The core of this project is to build a serverless, AI-powered "CV Ingestion Engine" using Python and the Azure OpenAI service, orchestrated by a Microsoft Power Automate workflow. This engine will replace the manual, time-consuming task of CV data entry with an automated, intelligent process that not only extracts basic information but also provides rich, analytical data to support faster and better hiring decisions.

The successful delivery of this module will provide a significant return on investment by drastically reducing administrative overhead for our HR team, standardizing candidate profiles, mitigating unconscious bias, and creating a rich, searchable talent pool for future needs.

### **2. The Business Problem & Current State**

Currently, our HR Representatives manually source CVs for approved Manpower Requisitions (MPRs). For each CV, they must:
1.  Read the entire document (PDF or DOCX).
2.  Manually extract key data points like name, contact info, experience, and skills.
3.  Create a new entry in our SharePoint-based "Candidate Tracker."
4.  Form a subjective, initial assessment of the candidate's suitability.

This process is slow, prone to data entry errors, lacks standardization, and creates a significant administrative burden that takes HR away from more strategic tasks like candidate engagement.

### **3. Proposed Solution: The "AI Ingestion Engine"**

We will build a serverless engine hosted on Azure Functions. This engine will be triggered by our Power Automate workflow whenever a new CV is uploaded to a designated SharePoint document library.

The engine's process is a **two-stage, privacy-centric pipeline:**

1.  **Stage 1 (PII Extraction & Redaction):** The engine will first process the CV to identify and separate Personally Identifiable Information (PII) from the professional/anonymized content.
2.  **Stage 2 (Skills & Experience Analysis):** The engine will then perform a deep analysis of the *anonymized* text to extract detailed professional history, skills, and analytical metrics.
3.  **Handoff:** The engine will return a single, comprehensive JSON object to the calling Power Automate flow, which will then populate our various SharePoint lists.

### **4. Detailed Functional Requirements**

The developer's primary task is to build a Python-based Azure Function that accomplishes the following.

#### **4.1. Input & Output**

*   **Input:** The function must accept an HTTP POST request with a JSON body containing:
    *   `fileName` (string): The name of the source file (e.g., "John_Smith_CV.pdf").
    *   `fileContent` (string): The Base64 encoded content of the CV file.
    *   `jobTitle` (string): The target job title from the parent MPR (e.g., "Senior Accountant").
*   **Output:** The function must return a single, valid JSON object. On success (HTTP 200), the object will have the structure defined in section 4.3. On failure (HTTP 500), it will have a structure like `{"processingStatus": "Failed", "errorDetails": "..."}`.

#### **4.2. Document Processing & Text Extraction**
*   The function must robustly handle both `.pdf` and `.docx` file types.
*   It must extract the textual content from these documents and convert it into a semantically rich **Markdown** format. The quality of this Markdown is critical for the accuracy of the subsequent AI analysis.
*   The implementation must include robust error handling for corrupt files, password-protected files, or files with no extractable text. The recommended library for PDF-to-Markdown is `pymupdf4llm`.

#### **4.3. The Three-Stage AI Pipeline: Privacy by Design**

The core of the function is to orchestrate a sophisticated, three-stage process that separates candidate data extraction, PII handling, and professional skills analysis. This approach ensures we collect necessary business data while maintaining our "Privacy by Design" and bias mitigation strategy.

##### **Stage 1: The `Candidate-Data-Extraction` Service Call**
*   **Purpose:** To extract structured candidate information required for business processes, including contact details, qualifications, and experience summaries.
*   **Implementation:** The developer will create a dedicated service module (e.g., `candidate_data_service.py`) that uses a **hybrid approach:**
    1.  **RegEx First:** Use robust regular expressions to find highly structured data (emails, phone numbers, LinkedIn URLs, portfolio links).
    2.  **LLM for Semantics:** Call a pre-configured Azure OpenAI Assistant, **`CV-Data-Extractor`**, to extract structured candidate information.
*   **Required JSON Output from the `CV-Data-Extractor` Assistant:**
    ```json
    {
      "candidateProfile": {
        "candidateName": "John Smith",
        "jobTitle": "Senior Marketing Manager",
        "status": "Active",
        "candidateEmail": "john.smith@email.com",
        "candidatePhone": "+1-555-123-4567",
        "linkedInUrl": "https://linkedin.com/in/johnsmith",
        "otherProfileUrls": ["https://johnsmith.dev", "https://github.com/johnsmith"],
        "currentLocation": "New York, NY",
        "currentTitle": "Senior Marketing Manager",
        "currentCompany": "Tech Innovations Inc",
        "professionalHeadline": "Experienced Marketing Professional with Digital Strategy Expertise",
        "totalExperienceYears": 8,
        "relevantExperienceYears": 6,
        "highestQualification": "Master of Business Administration",
        "currentSalary": "120000 USD",
        "expectedSalary": "140000 USD",
        "availabilityStatus": "Available in 30 days",
        "visaStatus": "Permanent Resident"
      }
    }
    ```

##### **Stage 2: The `PII-Identification` Service Call**
*   **Purpose:** To identify all Personally Identifiable Information (PII) in the CV text using AI, then programmatically generate an anonymized version to avoid hallucination issues.
*   **Implementation:** Using the same service module, call a separate Azure OpenAI Assistant, **`CV-PII-Identifier`**, to identify PII entities, then use Python code to create the anonymized text.
*   **Required JSON Output from the `CV-PII-Identifier` Assistant:**
    ```json
    {
      "pii_entities": [
        {
          "original_value": "John Smith",
          "pii_type": "name",
          "sensitivity_level": 4,
          "all_variations": ["John Smith", "John", "Smith"],
          "context": "candidate name in header",
          "region_specific": false
        },
        {
          "original_value": "Acme Corporation",
          "pii_type": "organization",
          "sensitivity_level": 2,
          "all_variations": ["Acme Corporation", "Acme Corp"],
          "context": "current employer",
          "region_specific": false
        },
        {
          "original_value": "Harvard University",
          "pii_type": "school",
          "sensitivity_level": 2,
          "all_variations": ["Harvard University", "Harvard"],
          "context": "education institution",
          "region_specific": false
        },
        {
          "original_value": "784-1985-1234567-8",
          "pii_type": "national_id",
          "sensitivity_level": 4,
          "all_variations": ["784-1985-1234567-8"],
          "context": "Emirates ID number",
          "region_specific": true
        }
      ]
    }
    ```
*   **JSON Schema for Function Tool (CV-PII-Identifier):**
    ```json
    {
      "type": "object",
      "properties": {
        "pii_entities": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "original_value": {
                "type": "string",
                "description": "Exact substring from the CV text"
              },
              "pii_type": {
                "type": "string",
                "enum": ["name", "address", "organization", "school", "job_title", "certification_number", "license_number", "national_id"],
                "description": "Type of PII detected"
              },
              "sensitivity_level": {
                "type": "integer",
                "minimum": 1,
                "maximum": 4,
                "description": "Sensitivity level (1=lowest, 4=highest)"
              },
              "all_variations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "All variations of this entity found in text"
              },
              "context": {
                "type": "string",
                "description": "Brief context where this PII was found"
              },
              "region_specific": {
                "type": "boolean",
                "description": "True if this is Middle Eastern specific PII"
              }
            },
            "required": ["original_value", "pii_type", "sensitivity_level", "all_variations", "context"]
          }
        }
      },
      "required": ["pii_entities"]
    }
    ```
*   **Programmatic Anonymization:** After receiving the PII entities from the assistant, the Python code will:
    1.  Generate deterministic placeholders for each PII type (e.g., `[CANDIDATE_NAME]`, `[COMPANY_1]`, `[UNIVERSITY_1]`)
    2.  Create a redaction mapping for reference
    3.  Perform text replacement using exact string matching to create the anonymized version
    4.  This approach eliminates LLM hallucination risks in the anonymized text generation

##### **Stage 3: The `Skills-and-Experience-Analyst` Assistant Call**
*   **Input to Assistant:** The **programmatically anonymized CV text** from Stage 2 and the `jobTitle` parameter.
*   **Action:** Call a third Azure OpenAI Assistant that focuses purely on professional analysis without access to identifying information.
*   **Required JSON Output from Assistant:**
    ```json
    {
      "analysisMetrics": {
        "aiConfidenceScore": 85,
        "aiRemarks": "Strong technical background with relevant industry experience...",
        "overallFitScore": 78
      },
      "professionalProfile": {
        "coreSkills": [
          { "skillName": "Project Management", "proficiencyLevel": "Expert", "yearsOfExperience": 5 },
          { "skillName": "Python", "proficiencyLevel": "Advanced", "yearsOfExperience": 3 }
        ],
        "workExperience": [
          {
            "jobTitle": "Senior Software Engineer",
            "companySize": "Large Enterprise",
            "duration": "3 years 2 months",
            "keyResponsibilities": ["Led development team", "Architected solutions"],
            "keyAchievements": ["Improved system performance by 40%", "Reduced deployment time"]
          }
        ],
        "educationProfile": {
          "highestDegreeLevel": "Masters",
          "fieldOfStudy": "Computer Science",
          "relevantCertifications": ["AWS Certified", "PMP Certified"]
        }
      }
    }
    ```

#### **4.4. Final Consolidated Output & AI Call Logging**
*   The function's final responsibility is to merge the outputs from all three stages, comprehensive AI call logging, and processing metadata into a single JSON object for Power Automate.
*   **CRITICAL REQUIREMENT:** All AI assistant calls must be logged with complete input prompts and responses to enable debugging, auditing, and potential re-running of specific stages.
*   **Final JSON structure to be returned to Power Automate:**
    ```json
    {
      "processingStatus": "Success",
      "processingMetadata": {
        "totalProcessingTimeMs": 12500,
        "fileName": "John_Smith_CV.pdf",
        "jobTitle": "Senior Software Engineer",
        "processedTimestamp": "2025-09-18T10:30:00Z"
      },
      "aiCallLogs": [
        {
          "stage": "candidate_data_extraction",
          "assistantId": "asst_xyz123",
          "modelUsed": "gpt-4",
          "inputPrompt": "Extract candidate information from the following CV text...",
          "inputTokens": 1200,
          "responseText": "{\"candidateProfile\": {...}}",
          "outputTokens": 300,
          "callDurationMs": 3500,
          "callTimestamp": "2025-09-18T10:30:01Z",
          "success": true,
          "errorDetails": null
        },
        {
          "stage": "pii_identification", 
          "assistantId": "asst_abc456",
          "modelUsed": "gpt-4",
          "inputPrompt": "Identify all PII entities in the following CV text...",
          "inputTokens": 1000,
          "responseText": "{\"pii_entities\": [...]}",
          "outputTokens": 400,
          "callDurationMs": 2800,
          "callTimestamp": "2025-09-18T10:30:05Z",
          "success": true,
          "errorDetails": null
        },
        {
          "stage": "skills_analysis",
          "assistantId": "asst_def789",
          "modelUsed": "gpt-4", 
          "inputPrompt": "Analyze the professional skills and experience...",
          "inputTokens": 800,
          "responseText": "{\"analysisMetrics\": {...}, \"professionalProfile\": {...}}",
          "outputTokens": 500,
          "callDurationMs": 4200,
          "callTimestamp": "2025-09-18T10:30:08Z",
          "success": true,
          "errorDetails": null
        }
      ],
      "candidateProfile": {
        "candidateName": "John Smith",
        "jobTitle": "Senior Software Engineer",
        "status": "Active",
        "candidateEmail": "john.smith@email.com",
        "candidatePhone": "+1-555-123-4567",
        "linkedInUrl": "https://linkedin.com/in/johnsmith",
        "otherProfileUrls": ["https://johnsmith.dev", "https://github.com/johnsmith"],
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
        "aiRemarks": "Strong technical background with relevant industry experience...",
        "overallFitScore": 78,
        "coreSkills": [
          { "skillName": "Project Management", "proficiencyLevel": "Expert", "yearsOfExperience": 5 }
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
      "tokenUsageSummary": {
        "totalInputTokens": 3000,
        "totalOutputTokens": 1200,
        "totalTokens": 4200,
        "estimatedCost": "0.042 USD"
      }
    }
    ```

#### **4.5. AI Call Logging Requirements**

*   **MANDATORY LOGGING:** Every call to an Azure OpenAI Assistant must be comprehensively logged to enable debugging, auditing, and potential re-execution.
*   **Required Log Elements for Each AI Call:**
    1.  **Stage Identification:** Clear identification of which processing stage (candidate_data_extraction, pii_identification, skills_analysis)
    2.  **Input Capture:** Complete input prompt text sent to the assistant (truncated if exceeding 10,000 characters)
    3.  **Response Capture:** Full response text received from the assistant
    4.  **Metadata:** Assistant ID, model used, token counts, timing, success status
    5.  **Error Handling:** Complete error details if the call fails
*   **Implementation Requirements:**
    *   Create a dedicated logging service class (e.g., `ai_call_logger.py`) 
    *   Log before and after each AI assistant call
    *   Store logs in structured format for easy parsing and analysis
    *   Include correlation IDs to track related calls within the same CV processing session
*   **Usage for Re-execution:** The logged data should be sufficient to replay any AI assistant call with the exact same inputs if needed for debugging or improvement purposes.

#### **4.6. Programmatic Anonymization Implementation**

*   **Anti-Hallucination Approach:** To address concerns about LLM hallucinations in text anonymization, the system uses a hybrid approach where AI only identifies PII locations, and Python code performs the actual text replacement.
*   **Implementation Steps:**
    1.  **PII Identification:** The `CV-PII-Identifier` assistant returns structured data about PII locations using the specified JSON schema
    2.  **Deterministic Placeholder Generation:** Python code generates consistent placeholders based on PII type and occurrence order (e.g., `[CANDIDATE_NAME]`, `[COMPANY_1]`, `[UNIVERSITY_1]`, `[COMPANY_2]`)
    3.  **Exact String Replacement:** Use Python's string replacement methods to substitute identified PII with placeholders
    4.  **Mapping Creation:** Maintain a redaction mapping for potential reverse operations or debugging
*   **Quality Assurance:**
    *   Validate that all identified PII entities are successfully replaced
    *   Ensure no original PII remains in the anonymized text
    *   Log any replacement failures for manual review
    *   Preserve document structure and readability in the anonymized version
*   **Benefits:**
    *   Eliminates LLM hallucination risks in anonymized text
    *   Ensures exact, reliable text replacement
    *   Maintains complete audit trail of what was replaced
    *   Enables consistent placeholder formatting across all CVs

#### **4.7. Prompt Engineering and Assistant Configuration**

*   **This is a core deliverable of the project.** The developer is not just responsible for writing Python code but is also expected to perform the expert task of **Prompt Engineering**.
*   This includes writing the detailed, robust "Instructions" (system prompts) for all three assistants in the Azure OpenAI Studio:
    1.  **`CV-Data-Extractor`**: Focused on extracting structured candidate information
    2.  **`CV-PII-Identifier`**: Specialized in identifying personal information (anonymization done programmatically)
    3.  **`CV-Skills-Analyst`**: Dedicated to professional skills and experience analysis
*   It also includes defining the precise **JSON Schemas** for the Function Tools that will be attached to each assistant to enforce the structured output.
*   The final prompts and schemas must be delivered as part of the project documentation.
*   **Key Design Principle**: Each assistant should have a single, focused responsibility to ensure optimal performance and maintainability.

#### **4.8. Specific Candidate Data Extraction Requirements**

The `CV-Data-Extractor` assistant must extract the following specific fields (these are mandatory for SharePoint integration):

*   **candidateName**: Full name of the candidate
*   **jobTitle**: The position they are applying for (from input parameter)
*   **status**: Processing status (typically "Active" for new extractions)
*   **candidateEmail**: Primary email address
*   **candidatePhone**: Primary phone number (with international format if available)
*   **linkedInUrl**: LinkedIn profile URL if available
*   **otherProfileUrls**: Array of other professional profiles (GitHub, portfolio sites, etc.)
*   **currentLocation**: Current city/country of residence
*   **currentTitle**: Current job title/position
*   **currentCompany**: Current employer name
*   **professionalHeadline**: Brief professional summary or headline
*   **totalExperienceYears**: Total years of professional experience (numeric)
*   **relevantExperienceYears**: Years of experience relevant to the target role (numeric)
*   **highestQualification**: Highest educational qualification achieved
*   **currentSalary**: Current salary information (with currency if mentioned)
*   **expectedSalary**: Expected salary information (with currency if mentioned)
*   **availabilityStatus**: When the candidate can start (e.g., "Immediate", "30 days notice")
*   **visaStatus**: Current visa/work authorization status

**Data Quality Requirements:**
*   All numeric fields (experience years, salary) should be extracted as numbers where possible
*   Salary information should include currency if mentioned in the CV
*   Phone numbers should be formatted consistently (international format preferred)
*   If any field is not available in the CV, return `null` or appropriate empty value
*   All extracted data must be exactly as it appears in the CV (no inference beyond reasonable interpretation)


### **5. Technical & Architectural Requirements**

*   **Language & Platform:** Python on Azure Functions (Consumption Plan).
*   **Modularity:** The code must be structured into separate, logical modules:
    -   `document_processor.py` (file parsing and text extraction)
    -   `candidate_data_service.py` (data extraction and PII redaction orchestration)
    -   `openai_service.py` (Azure OpenAI API interactions)
    -   `ai_call_logger.py` (comprehensive AI call logging and tracking)
    -   `__init__.py` (main Azure Function entry point)
*   **Security:** All secrets (API keys, Assistant IDs, Endpoints) must be read from Application Settings (Environment Variables). They must not be hard-coded.
*   **Error Handling:** The function must be highly resilient. It must include robust `try...except` blocks to handle file parsing errors, API call failures, timeouts, and invalid JSON responses from the AI. Failures should be logged and should return a proper HTTP 500 error with a descriptive JSON body.
*   **Logging:** Comprehensive logging (`logging.info`, `logging.error`) must be implemented throughout the code to provide visibility into the execution path and aid in debugging via Azure Application Insights.
*   **Dependencies:** All required Python libraries must be listed in a `requirements.txt` file.

### **6. Deliverables**

1.  A complete, well-documented, and production-ready Azure Functions project codebase, managed in our designated GitHub repository.
2.  **Comprehensive Assistant Configuration:**
    *   The final, engineered system prompts ("Instructions") for all three assistants:
        -   `CV-Data-Extractor` (candidate information extraction with all 18 required fields)
        -   `CV-PII-Identifier` (personal information identification - anonymization done programmatically)
        -   `CV-Skills-Analyst` (professional skills and experience analysis)
    *   The final, validated JSON Schemas for the Function Tool of each assistant.
3.  **AI Call Logging System:**
    *   Complete implementation of AI call logging with input/output capture
    *   Structured log format for debugging and re-execution capabilities
    *   Token usage tracking and cost estimation
4.  A `README.md` file within the project that explains how to:
    *   Create the three Assistants in Azure OpenAI Studio using the provided prompts and schemas.
    *   Configure all necessary environment variables (Endpoints, Keys, Assistant IDs).
    *   Deploy the Function App to Azure.
    *   Access and interpret the AI call logs for debugging purposes.

---

# Assistants Configuration Specification

**File:** `assistants.json`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Configuration Overview**

The `assistants.json` file serves as the centralized configuration for all AI assistants in the CV processing system. It contains prompts, JSON schemas, model parameters, and global settings in a single, version-controlled file that supports environment variable substitution and multi-environment deployments.

### **Core Purpose:**
- Centralized assistant configuration management
- Environment-specific settings with variable substitution
- Version-controlled prompts and schemas
- Model parameter configuration (temperature, max_tokens, etc.)
- Global system settings and defaults

## **2. File Structure and Schema**

### **2.1 Top-Level Structure**
```json
{
  "version": "1.0",
  "updated_at": "2025-09-23T10:30:00Z",
  "environment": "production",
  "assistants": {
    "cv_data_extractor": { /* Assistant Configuration */ },
    "cv_pii_identifier": { /* Assistant Configuration */ },
    "cv_skills_analyst": { /* Assistant Configuration */ }
  },
  "global_settings": {
    "api_version": "2024-05-01-preview",
    "timeout_seconds": 30,
    "max_retries": 3,
    "rate_limit_per_minute": 20
  }
}
```

### **2.2 Assistant Configuration Schema**
```json
{
  "assistant_id": "${CV_DATA_EXTRACTOR_ASSISTANT_ID}",
  "name": "Human-readable assistant name",
  "description": "Assistant purpose and functionality",
  "model": "gpt-4o-mini",
  "temperature": 0.1,
  "top_p": 1.0,
  "max_tokens": 2000,
  "instructions": "Complete system prompt with {variable} placeholders",
  "json_schema": {
    "type": "object",
    "properties": { /* JSON Schema Definition */ },
    "required": ["field1", "field2"]
  }
}
```

## **3. Complete Configuration File**

### **3.1 Full assistants.json Configuration**
```json
{
  "version": "1.0",
  "updated_at": "2025-09-23T10:30:00Z",
  "environment": "production",
  "description": "Centralized configuration for AI-powered CV processing assistants",
  
  "assistants": {
    "cv_data_extractor": {
      "assistant_id": "${CV_DATA_EXTRACTOR_ASSISTANT_ID}",
      "name": "CV Data Extractor",
      "description": "Extracts structured candidate information from CV text with high accuracy",
      "model": "gpt-4o-mini",
      "temperature": 0.1,
      "top_p": 1.0,
      "max_tokens": 2000,
      "instructions": "You are an expert HR data extraction specialist with deep knowledge of CV formats and candidate information patterns. Your task is to extract structured candidate information from the provided CV text with maximum accuracy and completeness.\n\n## Context\nTarget Job Title: {job_title}\n\n## Instructions\n1. Extract all available candidate information according to the JSON schema\n2. Focus on factual data extraction without inference or assumptions\n3. Return null for any field not explicitly found in the CV\n4. Be precise and accurate in your extraction\n5. Pay special attention to contact information, experience, and qualifications\n\n## Key Extraction Areas\n- **Contact Information**: Email, phone, LinkedIn, portfolio URLs\n- **Experience**: Total years and relevant years of experience\n- **Current Role**: Position, company, and professional headline\n- **Education**: Highest qualification achieved\n- **Compensation**: Current and expected salary information\n- **Availability**: Start date and visa/work authorization status\n- **Location**: Current city and country of residence\n\n## CV Text to Process\n{cv_text}\n\n## Output Requirements\n- Return data in the exact JSON schema format\n- Use null for missing information rather than empty strings\n- Ensure numeric fields (experience years) are returned as numbers\n- Include currency information with salary data if mentioned\n- Be consistent with formatting (e.g., phone number formats)\n\nExtract the candidate information now:",
      "json_schema": {
        "type": "object",
        "properties": {
          "candidateProfile": {
            "type": "object",
            "properties": {
              "candidateName": {
                "type": ["string", "null"],
                "description": "Full name of the candidate"
              },
              "jobTitle": {
                "type": "string",
                "description": "Target job title from input parameter"
              },
              "status": {
                "type": "string",
                "default": "Active",
                "description": "Candidate status for tracking"
              },
              "candidateEmail": {
                "type": ["string", "null"],
                "description": "Primary email address"
              },
              "candidatePhone": {
                "type": ["string", "null"],
                "description": "Primary phone number with international format if available"
              },
              "linkedInUrl": {
                "type": ["string", "null"],
                "description": "LinkedIn profile URL"
              },
              "otherProfileUrls": {
                "type": ["array", "null"],
                "items": {"type": "string"},
                "description": "Other professional profile URLs (GitHub, portfolio, etc.)"
              },
              "currentLocation": {
                "type": ["string", "null"],
                "description": "Current city and country of residence"
              },
              "currentTitle": {
                "type": ["string", "null"],
                "description": "Current job title or position"
              },
              "currentCompany": {
                "type": ["string", "null"],
                "description": "Current employer name"
              },
              "professionalHeadline": {
                "type": ["string", "null"],
                "description": "Professional summary or headline from CV"
              },
              "totalExperienceYears": {
                "type": ["number", "null"],
                "description": "Total years of professional experience"
              },
              "relevantExperienceYears": {
                "type": ["number", "null"],
                "description": "Years of experience relevant to target role"
              },
              "highestQualification": {
                "type": ["string", "null"],
                "description": "Highest educational qualification achieved"
              },
              "currentSalary": {
                "type": ["string", "null"],
                "description": "Current salary with currency if mentioned"
              },
              "expectedSalary": {
                "type": ["string", "null"],
                "description": "Expected salary with currency if mentioned"
              },
              "availabilityStatus": {
                "type": ["string", "null"],
                "description": "When candidate can start (e.g., 'Immediate', '30 days notice')"
              },
              "visaStatus": {
                "type": ["string", "null"],
                "description": "Current visa or work authorization status"
              }
            },
            "required": ["candidateName", "jobTitle", "status"]
          }
        },
        "required": ["candidateProfile"]
      }
    },
    
    "cv_pii_identifier": {
      "assistant_id": "${CV_PII_IDENTIFIER_ASSISTANT_ID}",
      "name": "CV PII Identifier",
      "description": "Identifies personally identifiable information in CV text for programmatic anonymization",
      "model": "gpt-4o-mini",
      "temperature": 0.0,
      "top_p": 1.0,
      "max_tokens": 1500,
      "instructions": "You are a privacy protection specialist with expertise in identifying Personally Identifiable Information (PII) across different cultural and regional contexts. Your task is to identify all PII in the provided CV text for programmatic anonymization.\n\n## Objective\nIdentify PII entities with exact substring matching for precise programmatic replacement. Focus on accuracy and completeness to ensure proper anonymization.\n\n## PII Categories to Identify\n\n### High Sensitivity (Level 4)\n- **Names**: Candidate name, references, emergency contacts, family members\n- **National IDs**: Emirates ID, Social Security Numbers, Passport numbers\n- **Personal Addresses**: Home addresses, specific street locations\n\n### Medium-High Sensitivity (Level 3)\n- **Organizations**: Current/previous employers (if identifying)\n- **Schools**: Universities, colleges, specific educational institutions\n- **Certification Numbers**: License numbers, professional certifications\n\n### Medium Sensitivity (Level 2)\n- **Job Titles**: If combined with company name could identify person\n- **Project Names**: Specific internal project names\n- **Client Names**: If mentioned in achievements or experience\n\n### Lower Sensitivity (Level 1)\n- **General Locations**: Cities, countries (evaluate in context)\n- **Industry Terms**: May be kept if not identifying\n\n## Regional Context Awareness\nPay special attention to Middle Eastern context:\n- Emirates ID numbers (format: 784-YYYY-NNNNNNN-N)\n- Arabic names and transliterations\n- Local company names and institutions\n- Wasta/Iqama numbers\n- Local educational institutions\n\n## Instructions\n1. Scan the entire CV text systematically\n2. Identify exact substrings that constitute PII\n3. Provide the exact text as it appears (critical for replacement)\n4. Include all variations of the same entity found in the text\n5. Classify each entity by type and sensitivity level\n6. Provide context for where each PII was found\n7. Mark region-specific PII appropriately\n\n## CV Text to Analyze\n{cv_text}\n\n## Output Requirements\n- Provide exact substrings as they appear in the original text\n- Include all variations of each PII entity\n- Assign appropriate sensitivity levels (1-4)\n- Be thorough but avoid false positives\n- Focus on information that could actually identify the individual\n\nAnalyze the CV text and identify all PII entities now:",
      "json_schema": {
        "type": "object",
        "properties": {
          "pii_entities": {
            "type": "array",
            "description": "Array of identified PII entities with metadata",
            "items": {
              "type": "object",
              "properties": {
                "original_value": {
                  "type": "string",
                  "description": "Exact substring from the CV text as it appears"
                },
                "pii_type": {
                  "type": "string",
                  "enum": [
                    "name", 
                    "address", 
                    "organization", 
                    "school", 
                    "job_title", 
                    "certification_number", 
                    "license_number", 
                    "national_id",
                    "project_name",
                    "client_name"
                  ],
                  "description": "Type of PII detected"
                },
                "sensitivity_level": {
                  "type": "integer",
                  "minimum": 1,
                  "maximum": 4,
                  "description": "Sensitivity level: 1=lowest, 4=highest"
                },
                "all_variations": {
                  "type": "array",
                  "items": {"type": "string"},
                  "description": "All variations of this entity found in the text"
                },
                "context": {
                  "type": "string",
                  "description": "Brief context describing where this PII was found"
                },
                "region_specific": {
                  "type": "boolean",
                  "description": "True if this is Middle Eastern or region-specific PII"
                }
              },
              "required": [
                "original_value", 
                "pii_type", 
                "sensitivity_level", 
                "all_variations", 
                "context"
              ]
            }
          }
        },
        "required": ["pii_entities"]
      }
    },
    
    "cv_skills_analyst": {
      "assistant_id": "${CV_SKILLS_ANALYST_ASSISTANT_ID}",
      "name": "CV Skills Analyst",
      "description": "Analyzes professional skills and experience from anonymized CV content",
      "model": "gpt-4o-mini",
      "temperature": 0.2,
      "top_p": 1.0,
      "max_tokens": 2500,
      "instructions": "You are a professional skills analysis expert and career assessment specialist. Your task is to analyze anonymized CV content to extract comprehensive professional qualifications, skills, and experience information while calculating fit scores for the target position.\n\n## Context\nTarget Job Title: {job_title}\n\n## Analysis Framework\n\n### 1. Core Skills Assessment\n- **Technical Skills**: Programming languages, software, tools, platforms\n- **Professional Skills**: Project management, leadership, communication\n- **Industry Skills**: Domain-specific knowledge and experience\n- **Proficiency Evaluation**: Assess skill levels based on experience context\n- **Experience Duration**: Years of experience per skill based on job history\n\n### 2. Work Experience Analysis\n- **Career Progression**: Analyze growth trajectory and advancement\n- **Company Context**: Assess company sizes and industry types\n- **Role Complexity**: Evaluate responsibilities and scope\n- **Achievements**: Identify quantifiable accomplishments\n- **Industry Relevance**: Match experience to target role requirements\n\n### 3. Education and Qualifications\n- **Degree Levels**: Assess educational background relevance\n- **Field Alignment**: Match education to target role requirements\n- **Certifications**: Professional certifications and ongoing learning\n- **Specialized Training**: Additional qualifications and courses\n\n### 4. Fit Assessment Methodology\n- **Overall Fit Score (0-100)**: Comprehensive match to target role\n- **Technical Fit**: Match of technical skills to requirements\n- **Experience Fit**: Relevance of work history\n- **Educational Fit**: Alignment of qualifications\n- **Growth Potential**: Candidate's learning trajectory\n\n## Scoring Guidelines\n\n### Overall Fit Score Ranges\n- **90-100**: Exceptional fit, exceeds requirements\n- **80-89**: Strong fit, meets most requirements well\n- **70-79**: Good fit, meets core requirements\n- **60-69**: Moderate fit, some gaps but potential\n- **50-59**: Fair fit, significant development needed\n- **Below 50**: Poor fit for the role\n\n### AI Confidence Score\nRate your confidence (0-100) in the analysis based on:\n- Clarity and detail of the anonymized CV content\n- Completeness of professional information available\n- Ability to assess fit for the specific target role\n\n## Anonymized CV Content to Analyze\n{anonymized_cv_text}\n\n## Analysis Requirements\n1. Provide objective, data-driven analysis\n2. Base assessments on evidence from the CV content\n3. Calculate realistic fit scores with justification\n4. Identify specific strengths and development areas\n5. Consider both current capabilities and growth potential\n6. Provide actionable insights for hiring decisions\n\nAnalyze the professional content and provide comprehensive assessment:",
      "json_schema": {
        "type": "object",
        "properties": {
          "analysisMetrics": {
            "type": "object",
            "properties": {
              "aiConfidenceScore": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "AI confidence level in analysis accuracy (0-100)"
              },
              "aiRemarks": {
                "type": "string",
                "description": "AI analysis summary with key observations and reasoning"
              },
              "overallFitScore": {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Overall candidate fit score for target role (0-100)"
              }
            },
            "required": ["aiConfidenceScore", "aiRemarks", "overallFitScore"]
          },
          "professionalProfile": {
            "type": "object",
            "properties": {
              "coreSkills": {
                "type": "array",
                "description": "Core professional and technical skills identified",
                "items": {
                  "type": "object",
                  "properties": {
                    "skillName": {
                      "type": "string",
                      "description": "Name of the skill"
                    },
                    "proficiencyLevel": {
                      "type": "string",
                      "enum": ["Beginner", "Intermediate", "Advanced", "Expert"],
                      "description": "Assessed proficiency level"
                    },
                    "yearsOfExperience": {
                      "type": "number",
                      "description": "Estimated years of experience with this skill"
                    }
                  },
                  "required": ["skillName", "proficiencyLevel", "yearsOfExperience"]
                }
              },
              "workExperience": {
                "type": "array",
                "description": "Structured work experience analysis",
                "items": {
                  "type": "object",
                  "properties": {
                    "jobTitle": {
                      "type": "string",
                      "description": "Job title or role (anonymized if needed)"
                    },
                    "companySize": {
                      "type": "string",
                      "enum": ["Startup", "Small", "Medium", "Large Enterprise"],
                      "description": "Estimated company size category"
                    },
                    "duration": {
                      "type": "string",
                      "description": "Duration in role (e.g., '2 years 3 months')"
                    },
                    "keyResponsibilities": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Key responsibilities and duties"
                    },
                    "keyAchievements": {
                      "type": "array",
                      "items": {"type": "string"},
                      "description": "Notable achievements and accomplishments"
                    }
                  },
                  "required": ["jobTitle", "companySize", "duration"]
                }
              },
              "educationProfile": {
                "type": "object",
                "properties": {
                  "highestDegreeLevel": {
                    "type": "string",
                    "enum": ["High School", "Associate", "Bachelor", "Masters", "PhD", "Professional"],
                    "description": "Highest educational qualification level"
                  },
                  "fieldOfStudy": {
                    "type": "string",
                    "description": "Primary field of study or specialization"
                  },
                  "relevantCertifications": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Professional certifications and credentials"
                  }
                },
                "required": ["highestDegreeLevel"]
              }
            },
            "required": ["coreSkills", "workExperience", "educationProfile"]
          }
        },
        "required": ["analysisMetrics", "professionalProfile"]
      }
    }
  },
  
  "global_settings": {
    "api_version": "2024-05-01-preview",
    "timeout_seconds": 30,
    "max_retries": 3,
    "rate_limit_per_minute": 20,
    "default_model": "gpt-4o-mini",
    "cost_optimization": {
      "enable_caching": true,
      "max_prompt_length": 50000,
      "max_response_length": 10000
    },
    "quality_settings": {
      "min_confidence_threshold": 70,
      "enable_response_validation": true,
      "enable_prompt_optimization": true
    }
  }
}
```

## **4. Environment Variable Substitution**

### **4.1 Variable Syntax**
- Use `${VARIABLE_NAME}` syntax for environment variable substitution
- Variables are resolved at runtime during configuration loading
- Unresolved variables will trigger warnings or errors

### **4.2 Required Environment Variables**
```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here

# Assistant IDs (created in Azure OpenAI Studio)
CV_DATA_EXTRACTOR_ASSISTANT_ID=asst_your_data_extractor_id
CV_PII_IDENTIFIER_ASSISTANT_ID=asst_your_pii_identifier_id
CV_SKILLS_ANALYST_ASSISTANT_ID=asst_your_skills_analyst_id
```

## **5. Configuration Management Best Practices**

### **5.1 Version Control**
- **Semantic Versioning**: Use semantic versioning for configuration changes
- **Change Tracking**: Document all changes in version control commits
- **Environment Branching**: Maintain separate configs for dev/staging/prod
- **Rollback Strategy**: Keep previous versions for easy rollback

### **5.2 Environment-Specific Configurations**
```json
// Development Environment
{
  "environment": "development",
  "assistants": {
    "cv_data_extractor": {
      "temperature": 0.3,  // Higher creativity for testing
      "max_tokens": 1500   // Lower limits for cost control
    }
  }
}

// Production Environment
{
  "environment": "production", 
  "assistants": {
    "cv_data_extractor": {
      "temperature": 0.1,  // Lower for consistency
      "max_tokens": 2000   // Higher for completeness
    }
  }
}
```

### **5.3 Validation and Testing**
- **Schema Validation**: Validate against JSON schema before deployment
- **Prompt Testing**: Test prompts with sample data before production
- **Performance Testing**: Validate token usage and response times
- **A/B Testing**: Test different prompt versions for optimization

## **6. Deployment and Maintenance**

### **6.1 Deployment Process**
1. **Configuration Validation**: Validate JSON structure and required fields
2. **Environment Variable Check**: Ensure all variables are available
3. **Assistant Verification**: Verify assistant IDs exist in Azure OpenAI
4. **Backup Previous Config**: Keep backup of current production config
5. **Deploy and Test**: Deploy with health checks and validation

### **6.2 Monitoring and Updates**
- **Performance Monitoring**: Track token usage and response quality
- **Cost Monitoring**: Monitor API costs and optimize parameters
- **Quality Metrics**: Track success rates and error patterns
- **Regular Reviews**: Periodic review and optimization of prompts

### **6.3 Security Considerations**
- **Sensitive Data**: Never include API keys or secrets in the config file
- **Access Control**: Restrict access to configuration files
- **Audit Trail**: Log all configuration changes
- **Environment Isolation**: Separate configs for different environments

## **7. Configuration Validation Schema**

### **7.1 JSON Schema for Configuration Validation**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "title": "AI Assistants Configuration Schema",
  "properties": {
    "version": {"type": "string", "pattern": "^\\d+\\.\\d+$"},
    "updated_at": {"type": "string", "format": "date-time"},
    "environment": {"type": "string", "enum": ["development", "staging", "production"]},
    "assistants": {
      "type": "object",
      "properties": {
        "cv_data_extractor": {"$ref": "#/definitions/assistant"},
        "cv_pii_identifier": {"$ref": "#/definitions/assistant"},
        "cv_skills_analyst": {"$ref": "#/definitions/assistant"}
      },
      "required": ["cv_data_extractor", "cv_pii_identifier", "cv_skills_analyst"]
    },
    "global_settings": {
      "type": "object",
      "properties": {
        "api_version": {"type": "string"},
        "timeout_seconds": {"type": "integer", "minimum": 10, "maximum": 300},
        "max_retries": {"type": "integer", "minimum": 1, "maximum": 10},
        "rate_limit_per_minute": {"type": "integer", "minimum": 1, "maximum": 100}
      },
      "required": ["api_version", "timeout_seconds", "max_retries"]
    }
  },
  "required": ["version", "assistants", "global_settings"],
  "definitions": {
    "assistant": {
      "type": "object",
      "properties": {
        "assistant_id": {"type": "string", "pattern": "^(asst_|\\$\\{)"},
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "model": {"type": "string", "enum": ["gpt-4o-mini", "gpt-4", "gpt-3.5-turbo"]},
        "temperature": {"type": "number", "minimum": 0, "maximum": 2},
        "top_p": {"type": "number", "minimum": 0, "maximum": 1},
        "max_tokens": {"type": "integer", "minimum": 1, "maximum": 16384},
        "instructions": {"type": "string", "minLength": 10},
        "json_schema": {"type": "object"}
      },
      "required": ["assistant_id", "name", "model", "instructions", "json_schema"]
    }
  }
}
```

## **8. Usage Examples**

### **8.1 Loading Configuration in Code**
```python
from shared_code.utils import load_assistant_config, get_assistant_prompt

# Load complete assistant configuration
extractor_config = load_assistant_config("cv_data_extractor")

# Get formatted prompt with variables
prompt = get_assistant_prompt(
    "cv_data_extractor",
    job_title="Senior Software Engineer",
    cv_text="CV content here..."
)

# Get JSON schema for validation
schema = get_assistant_schema("cv_data_extractor")
```

### **8.2 Environment-Specific Deployment**
```bash
# Development environment
export CV_DATA_EXTRACTOR_ASSISTANT_ID=asst_dev_extractor_123
export AZURE_OPENAI_ENDPOINT=https://dev-openai.openai.azure.com/

# Production environment  
export CV_DATA_EXTRACTOR_ASSISTANT_ID=asst_prod_extractor_456
export AZURE_OPENAI_ENDPOINT=https://prod-openai.openai.azure.com/
```

---

**Next Steps:**
- Create the complete assistants.json file in the project
- Implement configuration loading in utils.py
- Set up environment variable management
- Create validation scripts for configuration testing
- Establish deployment procedures for configuration updates
- Set up monitoring for configuration health and performance

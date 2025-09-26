# AI-Powered CV Processing Engine

[![Azure Functions](https://img.shields.io/badge/Azure-Functions-blue)](https://azure.microsoft.com/en-us/services/functions/)
[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-green)](https://openai.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

The **AI-Powered CV Processing Engine** is a serverless Azure Functions application that automates the extraction and analysis of candidate information from CVs. This intelligent system transforms manual data entry processes into an automated, privacy-centric pipeline that extracts structured candidate data, identifies PII, and performs comprehensive skills analysis.

### Key Features

- 🤖 **AI-Powered Processing**: Leverages Azure OpenAI GPT models for intelligent CV analysis
- 🔒 **Privacy by Design**: Three-stage pipeline with PII identification and anonymization
- 📄 **Multi-Format Support**: Processes PDF and DOCX files seamlessly
- ⚡ **Serverless Architecture**: Built on Azure Functions for scalability and cost-effectiveness
- 🔗 **Power Automate Integration**: Designed to work with Microsoft Power Automate workflows
- 📊 **Comprehensive Analytics**: Extracts 20+ data points including skills, experience, and qualifications
- 🧪 **Robust Testing**: Comprehensive test suite with unit and integration tests

## 🏗️ Architecture

The system implements a **three-stage AI pipeline**:

### Stage 1: Candidate Data Extraction
- Extracts structured candidate information (contact details, experience, qualifications)
- Uses hybrid approach: RegEx for structured data + LLM for semantic extraction
- Powered by `CV-Data-Extractor` Azure OpenAI Assistant

### Stage 2: PII Identification & Anonymization
- Identifies all Personally Identifiable Information using AI
- Creates anonymized versions for privacy-compliant processing
- Powered by `CV-PII-Identifier` Azure OpenAI Assistant

### Stage 3: Skills & Experience Analysis
- Performs deep analysis of anonymized content
- Extracts skills, competencies, and professional insights
- Powered by `CV-Skills-Analyst` Azure OpenAI Assistant

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Azure Functions Core Tools v4
- Azure OpenAI Service access
- Visual Studio Code (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_processing_azure_functions
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r test-requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp local.settings.json.template local.settings.json
   ```
   
   Edit `local.settings.json` with your Azure OpenAI credentials and assistant IDs.

5. **Run locally**
   ```bash
   func start
   ```

### Testing the API

The function exposes the following endpoints:

- **POST** `/api/process_cv` - Main CV processing endpoint
- **GET** `/api/health` - Health check endpoint

Example request:
```bash
curl -X POST http://localhost:7071/api/process_cv \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "john_doe_cv.pdf",
    "fileContent": "<base64-encoded-file-content>",
    "jobTitle": "Senior Software Engineer"
  }'
```

## 📋 API Reference

### Process CV Endpoint

**POST** `/api/process_cv`

#### Request Body
```json
{
  "fileName": "john_doe_cv.pdf",
  "fileContent": "base64-encoded-content",
  "jobTitle": "Senior Software Engineer"
}
```

#### Response (Success - 200)
```json
{
  "processingStatus": "Success",
  "candidateProfile": {
    "candidateName": "John Doe",
    "candidateEmail": "john.doe@email.com",
    "candidatePhone": "+1-555-123-4567",
    "currentTitle": "Software Engineer",
    "totalExperienceYears": 5,
    "highestQualification": "Bachelor of Science in Computer Science",
    // ... additional fields
  },
  "skillsAnalysis": {
    "technicalSkills": ["Python", "JavaScript", "React"],
    "softSkills": ["Leadership", "Communication"],
    "industryExperience": ["Software Development", "Web Development"],
    // ... additional analysis
  },
  "piiProcessing": {
    "anonymizedText": "CANDIDATE_NAME has X years of experience...",
    "piiEntitiesFound": 8,
    "anonymizationCompleted": true
  },
  "processingMetadata": {
    "processingTimeMs": 2500,
    "documentType": "pdf",
    "totalTokensUsed": 1250
  }
}
```

#### Response (Error - 500)
```json
{
  "processingStatus": "Failed",
  "errorDetails": "Error description",
  "errorCode": "PROCESSING_ERROR"
}
```

## 🗂️ Project Structure

```
ai_processing_azure_functions/
├── function_app.py              # Main Azure Function entry point
├── requirements.txt             # Production dependencies
├── test-requirements.txt        # Testing dependencies
├── host.json                   # Azure Functions host configuration
├── local.settings.json.template # Environment variables template
├── ENVIRONMENT_SETUP.md        # Setup instructions
├── pytest.ini                 # Test configuration
├── run_tests.py               # Test runner script
├── 
├── shared_code/               # Shared modules
│   ├── __init__.py
│   ├── ai_call_logger.py      # AI service call logging
│   ├── candidate_data_service.py  # Candidate data extraction
│   ├── document_processor.py  # Document processing utilities
│   ├── openai_service.py      # OpenAI service integration
│   └── utils.py               # General utilities
├── 
├── documentation/
│   └── GENESIS-DOCUMENT.md    # Project requirements and specifications
├── 
├── tests/                     # Test files
│   ├── test_cv_processing.py
│   ├── test_pii_anonymization.py
│   └── test_utilities.py
└── 
└── assistants.json           # Azure OpenAI Assistant configurations
```

## 🧪 Testing

The project includes comprehensive testing capabilities:

### Running Tests

```bash
# Run all tests
python run_tests.py

# Run specific test types
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type smoke

# Run with verbose output
python run_tests.py --verbose

# Run specific test files
pytest test_cv_processing.py -v
```

### Test Categories

- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test end-to-end workflows
- **Smoke Tests**: Quick validation of core functionality

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_API_VERSION` | API version (default: 2024-12-01-preview) | No |
| `CV_DATA_EXTRACTOR_ASSISTANT_ID` | Data extraction assistant ID | Yes |
| `CV_PII_IDENTIFIER_ASSISTANT_ID` | PII identification assistant ID | Yes |
| `CV_SKILLS_ANALYST_ASSISTANT_ID` | Skills analysis assistant ID | Yes |
| `PROCESSING_TIMEOUT_SECONDS` | Processing timeout (default: 30) | No |
| `MAX_FILE_SIZE_MB` | Maximum file size (default: 10) | No |
| `ENABLE_DEBUG_LOGGING` | Enable debug logging (default: false) | No |

### Azure OpenAI Assistants

The system requires three pre-configured Azure OpenAI Assistants:

1. **CV-Data-Extractor**: Extracts structured candidate information
2. **CV-PII-Identifier**: Identifies personally identifiable information
3. **CV-Skills-Analyst**: Analyzes skills and professional experience

Refer to `assistants.json` for assistant configurations and prompts.

## 🚀 Deployment

### Deploy to Azure

1. **Create Azure resources**
   ```bash
   az group create --name rg-cv-processing --location eastus
   az functionapp create --resource-group rg-cv-processing --consumption-plan-location eastus --runtime python --runtime-version 3.11 --functions-version 4 --name func-cv-processing --storage-account <storage-account>
   ```

2. **Deploy the function**
   ```bash
   func azure functionapp publish func-cv-processing
   ```

3. **Configure application settings**
   ```bash
   az functionapp config appsettings set --name func-cv-processing --resource-group rg-cv-processing --settings @local.settings.json
   ```

### CI/CD Pipeline

The project is ready for GitHub Actions or Azure DevOps pipelines. See `.github/workflows/` for example configurations.

## 📈 Monitoring & Logging

- **Application Insights**: Integrated for performance monitoring
- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Health Check Endpoint**: `/api/health` for monitoring systems
- **AI Call Logging**: Detailed tracking of OpenAI API usage

## 🔧 Troubleshooting

### Common Issues

1. **File Processing Errors**
   - Ensure files are properly base64 encoded
   - Check file size limits (default: 10MB)
   - Verify supported formats (PDF, DOCX)

2. **OpenAI Assistant Errors**
   - Verify assistant IDs are correct
   - Check API key permissions
   - Ensure assistants are properly configured

3. **Memory/Timeout Issues**
   - Adjust `PROCESSING_TIMEOUT_SECONDS`
   - Consider file size optimization
   - Monitor Azure Function memory usage

### Debug Mode

Enable debug logging by setting `ENABLE_DEBUG_LOGGING=true` in your environment variables.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Write comprehensive tests for new features
- Update documentation for API changes
- Use type hints for better code clarity

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For questions, issues, or contributions:

- **Project Lead**: Abu Huraira
- **Repository**: [GitHub Repository](https://github.com/ahuraira/integrated-hr-recruitment-tracker)
- **Issues**: [GitHub Issues](https://github.com/ahuraira/integrated-hr-recruitment-tracker/issues)

## 📚 Additional Documentation

- [Genesis Document](documentation/GENESIS-DOCUMENT.md) - Detailed project requirements and specifications  
- [Environment Setup](ENVIRONMENT_SETUP.md) - Detailed setup instructions
- [Test Documentation](TEST_README.md) - Comprehensive testing guide

---
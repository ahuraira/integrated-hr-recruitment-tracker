# CV Processing Engine - Comprehensive Test Suite

This comprehensive test suite provides thorough testing coverage for the AI-Powered CV Processing Engine, including all aspects of document processing, data extraction, PII anonymization, and AI service integration.

## 📋 Test Coverage

### Core Components Tested

1. **Document Processing** (`TestDocumentProcessor`)
   - PDF text extraction using `pymupdf4llm`
   - DOCX text extraction with proper Markdown conversion
   - Error handling for corrupt/unsupported files
   - Edge cases (empty documents, password-protected files)

2. **Candidate Data Extraction** (`TestCandidateDataService`)
   - Three-stage AI pipeline orchestration
   - RegEx-based structured data extraction
   - Azure OpenAI Assistant integration
   - Token usage calculation and cost estimation

3. **PII Identification & Anonymization** (`TestPIIIdentification`, `TestAnonymization`)
   - Comprehensive PII entity identification
   - Deterministic placeholder generation
   - Multi-language and region-specific PII handling
   - Complete anonymization verification
   - Privacy compliance testing

4. **AI Service Integration** (`TestOpenAIService`)
   - Azure OpenAI client configuration
   - Assistant API calls and response handling
   - Error handling and timeout management
   - Authentication and authorization

5. **AI Call Logging** (`TestAICallLogger`)
   - Comprehensive call logging with input/output capture
   - Token usage tracking
   - Error logging and debugging support
   - Performance metrics collection

6. **Function App Integration** (`TestFunctionApp`)
   - HTTP request validation and parsing
   - Configuration validation
   - Base64 encoding/decoding
   - End-to-end workflow testing

7. **Error Handling** (`TestErrorHandling`)
   - Comprehensive error scenarios
   - Exception handling and recovery
   - Graceful degradation testing
   - Error logging and reporting

8. **Performance Testing** (`TestPerformance`)
   - Large document processing
   - Multiple PII entity handling
   - Load testing scenarios
   - Memory usage optimization

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Install test dependencies**:
   ```powershell
   pip install -r test-requirements.txt
   ```

3. **Set up test environment** (automatically handled by test runner):
   ```powershell
   # Test environment variables are set automatically
   # No real Azure OpenAI credentials needed for testing
   ```

### Running Tests

#### Option 1: Using the Test Runner (Recommended)

```powershell
# Run all tests with coverage
python run_tests.py --type all

# Run specific test types
python run_tests.py --type unit          # Unit tests only
python run_tests.py --type integration   # Integration tests only
python run_tests.py --type pii          # PII and anonymization tests
python run_tests.py --type error        # Error handling tests
python run_tests.py --type performance  # Performance tests
python run_tests.py --type smoke        # Quick smoke tests

# Run specific test pattern
python run_tests.py --type specific --pattern "test_extract_markdown"

# Validate dependencies only
python run_tests.py --validate-deps
```

#### Option 2: Using pytest directly

```powershell
# Run all tests
python -m pytest test_cv_processing.py test_pii_anonymization.py -v

# Run with coverage
python -m pytest --cov=shared_code --cov-report=html --cov-report=term-missing

# Run specific test class
python -m pytest test_cv_processing.py::TestDocumentProcessor -v

# Run specific test method
python -m pytest test_cv_processing.py::TestDocumentProcessor::test_extract_markdown_from_pdf_success -v
```

## 📊 Test Reports

After running tests, you'll find detailed reports in the `reports/` directory:

- **`htmlcov/index.html`** - Interactive HTML coverage report
- **`pytest_report.html`** - Detailed test execution report  
- **`junit.xml`** - JUnit XML format for CI/CD integration
- **`report.json`** - JSON format test results
- **`coverage.xml`** - XML coverage report

## 🧪 Test Structure

### Test Files

1. **`test_cv_processing.py`** - Main test suite covering all core functionality
2. **`test_pii_anonymization.py`** - Specialized PII and anonymization tests
3. **`test_utilities.py`** - Test utilities, fixtures, and helper functions
4. **`run_tests.py`** - Comprehensive test runner script

### Test Categories

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests for component interactions
- `@pytest.mark.pii` - PII identification and anonymization tests
- `@pytest.mark.performance` - Performance and load tests
- `@pytest.mark.error` - Error handling and edge case tests

## 🔧 Test Configuration

### Environment Variables

The test suite uses mock environment variables automatically:

```python
AZURE_OPENAI_ENDPOINT = "https://test-openai.openai.azure.com/"
AZURE_OPENAI_API_KEY = "test-api-key-12345"
CV_DATA_EXTRACTOR_ASSISTANT_ID = "asst_cv_data_extractor_test"
CV_PII_IDENTIFIER_ASSISTANT_ID = "asst_pii_identifier_test"
CV_SKILLS_ANALYST_ASSISTANT_ID = "asst_skills_analyst_test"
```

### Test Data

The test suite includes comprehensive test data:

- **Sample CV content** in multiple formats and languages
- **Complex PII scenarios** with edge cases
- **Mock AI responses** for all three assistant types
- **Edge case documents** with special characters and formatting

## 📋 Test Scenarios Covered

### Document Processing Tests

✅ PDF text extraction success and failure cases  
✅ DOCX text extraction with formatting preservation  
✅ Unsupported file type handling  
✅ Empty document detection  
✅ Corrupt file error handling  
✅ Large document processing  

### Data Extraction Tests

✅ RegEx-based structured data extraction (emails, phones, URLs)  
✅ AI-powered candidate profile extraction  
✅ Hybrid extraction approach (RegEx + AI)  
✅ Missing data handling (null values)  
✅ Data validation and sanitization  

### PII Anonymization Tests

✅ Basic PII identification (names, companies, schools)  
✅ Complex PII scenarios (titles, suffixes, variations)  
✅ Multilingual PII handling (Arabic, English)  
✅ Region-specific PII (Emirates ID, SSN, etc.)  
✅ Deterministic placeholder generation  
✅ Complete PII removal verification  
✅ Document structure preservation  
✅ High-sensitivity PII handling (level 4)  
✅ Overlapping entity variations  
✅ Edge cases (special characters, hyphens, apostrophes)  

### AI Service Tests

✅ OpenAI service initialization and configuration  
✅ Assistant API calls and response handling  
✅ Error handling for failed API calls  
✅ Token usage tracking and cost calculation  
✅ Timeout and retry logic  
✅ Response parsing and validation  

### Integration Tests

✅ End-to-end CV processing workflow  
✅ Three-stage AI pipeline orchestration  
✅ Component interaction and data flow  
✅ Error propagation and handling  
✅ Performance under load  

### Error Handling Tests

✅ Invalid input handling  
✅ API service failures  
✅ Network timeout scenarios  
✅ JSON parsing errors  
✅ Configuration validation errors  
✅ Graceful degradation  

## 🎯 Coverage Goals

The test suite aims for:

- **>95% Code Coverage** for core business logic
- **>85% Branch Coverage** for all conditional paths
- **100% Error Path Coverage** for exception handling
- **Complete API Coverage** for all public methods

## 📈 Performance Benchmarks

Performance tests validate:

- **Document Processing**: <5 seconds for 100KB documents
- **PII Anonymization**: <2 seconds for 100 PII entities
- **AI Pipeline**: <30 seconds for complete processing
- **Memory Usage**: <100MB for typical CV processing

## 🔍 Debugging Tests

### Running Individual Tests

```powershell
# Run a specific test with detailed output
python -m pytest test_cv_processing.py::TestDocumentProcessor::test_extract_markdown_from_pdf_success -v -s

# Run with pdb debugger
python -m pytest test_cv_processing.py::TestDocumentProcessor::test_extract_markdown_from_pdf_success -v -s --pdb
```

### Viewing Test Logs

```powershell
# Run with logging output
python -m pytest test_cv_processing.py -v -s --log-cli-level=INFO
```

### Mock Debugging

The test suite includes comprehensive mocking. To debug mock calls:

```python
# Add this to test methods for debugging
print(f"Mock called with: {mock_object.call_args_list}")
```

## 🚨 Common Issues and Solutions

### Issue: Tests fail with import errors
**Solution**: Ensure you're in the correct directory and have installed test dependencies:
```powershell
cd ai_processing_azure_functions
pip install -r test-requirements.txt
```

### Issue: "No tests ran matching the given pattern"
**Solution**: Check test file names and method names match pytest conventions (start with `test_`)

### Issue: Coverage reports show 0% coverage
**Solution**: Ensure the `shared_code` module is in Python path:
```powershell
set PYTHONPATH=%CD%
python -m pytest --cov=shared_code
```

### Issue: Mock objects not working as expected
**Solution**: Verify patch targets match the actual import paths in the code being tested

## 📚 Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **pytest-cov**: https://pytest-cov.readthedocs.io/
- **unittest.mock**: https://docs.python.org/3/library/unittest.mock.html
- **Azure OpenAI Testing**: https://docs.microsoft.com/en-us/azure/cognitive-services/openai/

## 🤝 Contributing to Tests

When adding new functionality:

1. **Write tests first** (TDD approach)
2. **Cover happy path and edge cases**
3. **Add appropriate pytest markers**
4. **Update this README** if adding new test categories
5. **Ensure >80% coverage** for new code
6. **Add test data** to `test_utilities.py` if needed

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*`
- Test methods: `test_*`
- Use descriptive names: `test_extract_candidate_profile_with_missing_email`

### Mock Usage Guidelines

- **Mock external dependencies** (OpenAI API, file system)
- **Don't mock the code under test**
- **Use appropriate mock return values** that match real API responses
- **Verify mock calls** when testing integration points

---

## 📊 Current Test Statistics

- **Total Test Files**: 3
- **Total Test Classes**: 15+
- **Total Test Methods**: 100+
- **Expected Coverage**: >90%
- **Test Execution Time**: ~30 seconds for full suite

This comprehensive test suite ensures the CV Processing Engine is robust, reliable, and ready for production use. 🚀

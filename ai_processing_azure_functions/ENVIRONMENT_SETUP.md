# Environment Setup Instructions

## 🔧 Initial Setup

### 1. Create Local Settings File
Copy the template and configure your environment:
```bash
cp local.settings.json.template local.settings.json
```

### 2. Configure API Keys and Settings
Edit `local.settings.json` with your actual values:

- **AZURE_OPENAI_ENDPOINT**: Your Azure OpenAI service endpoint
- **AZURE_OPENAI_API_KEY**: Your Azure OpenAI API key
- **CV_DATA_EXTRACTOR_ASSISTANT_ID**: Your data extractor assistant ID
- **CV_PII_IDENTIFIER_ASSISTANT_ID**: Your PII identifier assistant ID  
- **CV_SKILLS_ANALYST_ASSISTANT_ID**: Your skills analyst assistant ID

### 3. Install Dependencies
```bash
pip install -r requirements.txt
pip install -r test-requirements.txt
```

### 4. Run Tests
```bash
python run_tests.py --type smoke
```

## ⚠️ Security Notes

- **NEVER** commit `local.settings.json` to version control
- Keep API keys secure and rotate them regularly
- Use environment variables in production deployments

## 📁 Ignored Files

The following files are automatically ignored by git:
- `local.settings.json` - Contains sensitive API keys
- `azure_assistant_summary.json` - Contains assistant configuration
- `reports/` - Test reports and coverage data
- `__pycache__/` - Python bytecode cache
- `.coverage` - Coverage data files

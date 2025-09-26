# 🚀 Azure Functions Deployment Guide
## AI-Powered CV Processing Engine

This guide provides multiple methods to deploy your CV processing function app to Azure Functions.

## 📋 Prerequisites

### ✅ **1. Required Tools Installation**

#### Azure Functions Core Tools (✅ Installed)
```bash
# Already installed - Version 4.2.2
func --version
```

#### Azure CLI (Required for CLI deployment)
```bash
# Install Azure CLI
# Windows (PowerShell as Administrator):
Invoke-WebRequest -Uri https://aka.ms/installazurecliwindows -OutFile .\AzureCLI.msi; Start-Process msiexec.exe -Wait -ArgumentList '/I AzureCLI.msi /quiet'; rm .\AzureCLI.msi

# Verify installation
az --version
```

### ✅ **2. Azure Resources Required**

Before deployment, ensure you have:
- Azure Subscription
- Resource Group
- Storage Account
- Azure Functions App (Python 3.11)
- Azure OpenAI Service configured

---

## 🚀 **Method 1: Azure Functions Core Tools (Recommended)**

### **Step 1: Login to Azure**
```bash
az login
```

### **Step 2: Create Azure Resources**
```bash
# Set variables
$resourceGroup = "rg-cv-processing"
$location = "East US"
$storageAccount = "stcvprocessing$(Get-Random)"
$functionApp = "func-cv-processing-$(Get-Random)"

# Create resource group
az group create --name $resourceGroup --location $location

# Create storage account
az storage account create `
  --name $storageAccount `
  --location $location `
  --resource-group $resourceGroup `
  --sku Standard_LRS

# Create function app
az functionapp create `
  --resource-group $resourceGroup `
  --consumption-plan-location $location `
  --runtime python `
  --runtime-version 3.11 `
  --functions-version 4 `
  --name $functionApp `
  --storage-account $storageAccount
```

### **Step 3: Configure Application Settings**
```bash
# Navigate to function directory
cd ai_processing_azure_functions

# Configure app settings (replace with your actual values)
az functionapp config appsettings set `
  --name $functionApp `
  --resource-group $resourceGroup `
  --settings `
    AZURE_OPENAI_ENDPOINT="https://your-openai-endpoint.openai.azure.com/" `
    AZURE_OPENAI_API_KEY="your-api-key" `
    AZURE_OPENAI_API_VERSION="2024-12-01-preview" `
    CV_DATA_EXTRACTOR_ASSISTANT_ID="your-extractor-id" `
    CV_PII_IDENTIFIER_ASSISTANT_ID="your-pii-id" `
    CV_SKILLS_ANALYST_ASSISTANT_ID="your-skills-id" `
    PROCESSING_TIMEOUT_SECONDS="30" `
    MAX_FILE_SIZE_MB="10" `
    ENABLE_DEBUG_LOGGING="false"
```

### **Step 4: Deploy Function**
```bash
# Deploy the function app
func azure functionapp publish $functionApp
```

---

## 🚀 **Method 2: VS Code Extension (Easy)**

### **Step 1: Install VS Code Extension**
1. Install "Azure Functions" extension in VS Code
2. Install "Azure Account" extension

### **Step 2: Deploy**
1. Open VS Code in `ai_processing_azure_functions` folder
2. Press `Ctrl+Shift+P` → "Azure Functions: Deploy to Function App"
3. Select your Azure subscription
4. Choose "Create new Function App in Azure"
5. Configure settings and deploy

---

## 🚀 **Method 3: ZIP Deployment**

### **Step 1: Create Deployment Package**
```bash
# Navigate to function directory
cd ai_processing_azure_functions

# Create deployment package (exclude test files and sensitive data)
$excludeItems = @(
    "local.settings.json",
    "azure_assistant_summary.json", 
    "reports",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "test_*.py",
    "run_tests.py",
    "TEST_README.md"
)

# Create zip package
Compress-Archive -Path * -DestinationPath "../cv-processing-function.zip" -Force
```

### **Step 2: Deploy via Azure Portal**
1. Go to Azure Portal → Your Function App
2. Navigate to "Deployment Center"
3. Select "ZIP Deploy"
4. Upload `cv-processing-function.zip`

---

## 🚀 **Method 4: GitHub Actions (CI/CD)**

### **Step 1: Create GitHub Workflow**
Create `.github/workflows/azure-functions-deploy.yml`:

```yaml
name: Deploy Azure Functions

on:
  push:
    branches: [ main ]
    paths: 
      - 'ai_processing_azure_functions/**'

env:
  AZURE_FUNCTIONAPP_NAME: 'func-cv-processing'
  AZURE_FUNCTIONAPP_PACKAGE_PATH: './ai_processing_azure_functions'
  PYTHON_VERSION: '3.11'

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
    - name: 'Checkout GitHub Action'
      uses: actions/checkout@v4

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: 'Install dependencies'
      shell: bash
      run: |
        cd ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: 'Run tests'
      shell: bash
      run: |
        cd ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        pip install -r test-requirements.txt
        python run_tests.py --type smoke

    - name: 'Deploy to Azure Functions'
      uses: Azure/functions-action@v1
      with:
        app-name: ${{ env.AZURE_FUNCTIONAPP_NAME }}
        package: ${{ env.AZURE_FUNCTIONAPP_PACKAGE_PATH }}
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

### **Step 2: Configure Secrets**
1. Get publish profile from Azure Portal
2. Add `AZURE_FUNCTIONAPP_PUBLISH_PROFILE` to GitHub Secrets

---

## ⚙️ **Post-Deployment Configuration**

### **1. Environment Variables**
Ensure these are configured in Azure:
```
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_API_VERSION
CV_DATA_EXTRACTOR_ASSISTANT_ID
CV_PII_IDENTIFIER_ASSISTANT_ID
CV_SKILLS_ANALYST_ASSISTANT_ID
PROCESSING_TIMEOUT_SECONDS
MAX_FILE_SIZE_MB
ENABLE_DEBUG_LOGGING
```

### **2. Function URL**
After deployment, your function will be available at:
```
https://your-function-app.azurewebsites.net/api/process_cv
```

### **3. API Testing**
Test your deployed function:
```bash
# Test with curl
curl -X POST "https://your-function-app.azurewebsites.net/api/process_cv" `
  -H "Content-Type: application/json" `
  -d '{
    "fileName": "test.pdf",
    "fileContent": "base64-encoded-content",
    "jobTitle": "Software Engineer"
  }'
```

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **Module Import Errors**
   - Ensure `requirements.txt` includes all dependencies
   - Check Python version compatibility (3.11)

2. **Environment Variables**
   - Verify all required settings are configured
   - Check for typos in variable names

3. **Timeout Issues**
   - Increase `PROCESSING_TIMEOUT_SECONDS`
   - Consider Premium plan for longer timeouts

4. **Memory Issues**
   - Optimize large document processing
   - Consider Premium plan for more memory

### **Monitoring & Logs**
- Use Application Insights for monitoring
- Check Function App logs in Azure Portal
- Enable diagnostic logging for debugging

---

## 🎯 **Next Steps**

1. **Security**: Configure CORS and authentication
2. **Monitoring**: Set up Application Insights
3. **Scaling**: Configure auto-scaling rules
4. **Backup**: Set up backup strategies
5. **CI/CD**: Implement automated deployments

Your AI-powered CV processing function is now ready for production! 🚀

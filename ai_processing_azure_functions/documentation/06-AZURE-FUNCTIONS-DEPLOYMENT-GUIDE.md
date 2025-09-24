# Azure Functions Setup and Deployment Guide

**Project:** AI-Powered CV Processing Engine  
**Version:** 1.0  
**Date:** September 23, 2025  
**Target:** Azure Functions Python 3.9+ Runtime

## **1. Prerequisites**

### **1.1 Required Software**
- **Azure CLI** v2.50.0 or later
- **Azure Functions Core Tools** v4.0 or later
- **Python** 3.9, 3.10, or 3.11
- **Git** for version control
- **VS Code** with Azure Functions extension (recommended)

### **1.2 Azure Subscription Requirements**
- Active Azure subscription
- Resource Group creation permissions
- Azure Functions and Azure OpenAI service permissions
- Storage Account creation permissions

## **2. Azure Resources Setup**

### **2.1 Create Resource Group**
```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "your-subscription-id"

# Create resource group
az group create \
  --name "rg-hr-cv-processing" \
  --location "East US"
```

### **2.2 Create Storage Account**
```bash
# Create storage account (required for Azure Functions)
az storage account create \
  --name "sthrcdprocessing$(date +%s)" \
  --resource-group "rg-hr-cv-processing" \
  --location "East US" \
  --sku "Standard_LRS" \
  --kind "StorageV2"
```

### **2.3 Create Azure OpenAI Service**
```bash
# Create Azure OpenAI service
az cognitiveservices account create \
  --name "openai-hr-cv-processing" \
  --resource-group "rg-hr-cv-processing" \
  --location "East US" \
  --kind "OpenAI" \
  --sku "S0"
```

### **2.4 Create Function App**
```bash
# Create Function App
az functionapp create \
  --resource-group "rg-hr-cv-processing" \
  --consumption-plan-location "East US" \
  --runtime "python" \
  --runtime-version "3.11" \
  --functions-version "4" \
  --name "func-hr-cv-processing-$(date +%s)" \
  --storage-account "sthrcdprocessing$(date +%s)" \
  --os-type "Linux"
```

## **3. Azure OpenAI Assistant Setup**

### **3.1 Deploy Models**
```bash
# Deploy GPT-4o-mini model
az cognitiveservices account deployment create \
  --resource-group "rg-hr-cv-processing" \
  --name "openai-hr-cv-processing" \
  --deployment-name "gpt-4o-mini" \
  --model-name "gpt-4o-mini" \
  --model-version "2024-07-18" \
  --model-format "OpenAI" \
  --sku-capacity 10 \
  --sku-name "Standard"
```

### **3.2 Create AI Assistants**

#### **Option A: Using Azure OpenAI Studio (Recommended)**
1. Navigate to [Azure OpenAI Studio](https://oai.azure.com/)
2. Select your Azure OpenAI resource
3. Go to **Assistants** section
4. Create three assistants with the configurations from `assistants.json`

#### **Option B: Using Python Script**
```python
# create_assistants.py
import os
from openai import AzureOpenAI
import json

# Initialize client
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview"
)

# Load assistant configurations
with open('assistants.json', 'r') as f:
    config = json.load(f)

# Create assistants
for assistant_name, assistant_config in config['assistants'].items():
    assistant = client.beta.assistants.create(
        name=assistant_config['name'],
        instructions=assistant_config['instructions'],
        model=assistant_config['model'],
        tools=[{
            "type": "function",
            "function": {
                "name": "extract_data",
                "description": assistant_config['description'],
                "parameters": assistant_config['json_schema']
            }
        }],
        temperature=assistant_config['temperature']
    )
    
    print(f"Created {assistant_name}: {assistant.id}")
```

## **4. Local Development Setup**

### **4.1 Project Structure Setup**
```bash
# Clone your repository
git clone https://github.com/ahuraira/integrated-hr-recruitment-tracker.git
cd integrated-hr-recruitment-tracker/ai_processing_azure_functions

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Azure Functions Core Tools (if not installed)
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

### **4.2 Local Configuration**
Create or update `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_ENDPOINT": "https://openai-hr-cv-processing.openai.azure.com/",
    "AZURE_OPENAI_API_KEY": "your-azure-openai-api-key",
    "CV_DATA_EXTRACTOR_ASSISTANT_ID": "asst_your_data_extractor_id",
    "CV_PII_IDENTIFIER_ASSISTANT_ID": "asst_your_pii_identifier_id",
    "CV_SKILLS_ANALYST_ASSISTANT_ID": "asst_your_skills_analyst_id",
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "your-app-insights-connection-string",
    "PROCESSING_TIMEOUT_SECONDS": "30",
    "MAX_FILE_SIZE_MB": "10",
    "ENABLE_DEBUG_LOGGING": "true"
  }
}
```

### **4.3 Test Local Development**
```bash
# Start Azure Functions locally
func start

# Test the function
curl -X POST http://localhost:7071/api/process_cv \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "test_cv.pdf",
    "fileContent": "base64_encoded_content_here",
    "jobTitle": "Software Engineer"
  }'
```

## **5. Deployment Process**

### **5.1 Prepare for Deployment**
```bash
# Ensure all dependencies are in requirements.txt
pip freeze > requirements.txt

# Add Azure Function specific dependencies
echo "azure-functions" >> requirements.txt
echo "azure-functions-worker" >> requirements.txt

# Commit your changes
git add .
git commit -m "Prepare for Azure deployment"
git push origin main
```

### **5.2 Deploy to Azure**

#### **Option A: Using Azure CLI (Recommended)**
```bash
# Deploy function app
func azure functionapp publish func-hr-cv-processing-$(date +%s) --python

# Alternative with specific function app name
func azure functionapp publish your-function-app-name --python
```

#### **Option B: Using VS Code**
1. Install Azure Functions extension
2. Sign in to Azure
3. Right-click on function project
4. Select "Deploy to Function App"
5. Choose your subscription and function app

#### **Option C: Using GitHub Actions (CI/CD)**
Create `.github/workflows/azure-functions-deploy.yml`:
```yaml
name: Deploy Azure Functions

on:
  push:
    branches: [ main ]
    paths: [ 'ai_processing_azure_functions/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd ai_processing_azure_functions
        pip install -r requirements.txt
    
    - name: Deploy to Azure Functions
      uses: Azure/functions-action@v1
      with:
        app-name: 'your-function-app-name'
        package: './ai_processing_azure_functions'
        publish-profile: ${{ secrets.AZURE_FUNCTIONAPP_PUBLISH_PROFILE }}
```

### **5.3 Configure Application Settings**
```bash
# Set application settings (environment variables)
az functionapp config appsettings set \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --settings \
    "AZURE_OPENAI_ENDPOINT=https://openai-hr-cv-processing.openai.azure.com/" \
    "AZURE_OPENAI_API_KEY=your-azure-openai-api-key" \
    "CV_DATA_EXTRACTOR_ASSISTANT_ID=asst_your_data_extractor_id" \
    "CV_PII_IDENTIFIER_ASSISTANT_ID=asst_your_pii_identifier_id" \
    "CV_SKILLS_ANALYST_ASSISTANT_ID=asst_your_skills_analyst_id" \
    "PROCESSING_TIMEOUT_SECONDS=30" \
    "MAX_FILE_SIZE_MB=10"
```

## **6. Post-Deployment Configuration**

### **6.1 Enable Application Insights**
```bash
# Create Application Insights
az monitor app-insights component create \
  --app "appinsights-hr-cv-processing" \
  --location "East US" \
  --resource-group "rg-hr-cv-processing"

# Get connection string
az monitor app-insights component show \
  --app "appinsights-hr-cv-processing" \
  --resource-group "rg-hr-cv-processing" \
  --query "connectionString" -o tsv

# Add to function app settings
az functionapp config appsettings set \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --settings "APPLICATIONINSIGHTS_CONNECTION_STRING=your-connection-string"
```

### **6.2 Configure Function Authentication (Optional)**
```bash
# Enable function-level authentication
az functionapp auth update \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --enabled true \
  --action "LoginWithAzureActiveDirectory"
```

### **6.3 Set up CORS (if needed for web testing)**
```bash
az functionapp cors add \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --allowed-origins "https://make.powerapps.com" "https://make.powerautomate.com"
```

## **7. Testing and Validation**

### **7.1 Function URL and Testing**
```bash
# Get function URL
az functionapp function show \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --function-name "process_cv" \
  --query "invokeUrlTemplate" -o tsv

# Test deployed function
curl -X POST "https://your-function-app-name.azurewebsites.net/api/process_cv?code=your-function-key" \
  -H "Content-Type: application/json" \
  -d '{
    "fileName": "test_cv.pdf",
    "fileContent": "base64_encoded_content_here",
    "jobTitle": "Software Engineer"
  }'
```

### **7.2 Monitor Function Performance**
```bash
# View function logs
az functionapp log tail \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing"

# Check function metrics
az monitor metrics list \
  --resource "/subscriptions/your-subscription-id/resourceGroups/rg-hr-cv-processing/providers/Microsoft.Web/sites/your-function-app-name" \
  --metric "FunctionExecutionCount"
```

## **8. Power Automate Integration**

### **8.1 Get Function URL for Power Automate**
1. Go to Azure Portal → Function App → Functions → process_cv
2. Click "Get Function Url"
3. Copy the URL with the function key
4. Use this URL in Power Automate HTTP action

### **8.2 Power Automate HTTP Action Configuration**
```json
{
  "method": "POST",
  "uri": "https://your-function-app-name.azurewebsites.net/api/process_cv?code=your-function-key",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "fileName": "@{triggerBody()['fileName']}",
    "fileContent": "@{base64(triggerBody()['fileContent'])}",
    "jobTitle": "@{triggerBody()['jobTitle']}"
  }
}
```

## **9. Monitoring and Maintenance**

### **9.1 Set up Alerts**
```bash
# Create alert for function failures
az monitor metrics alert create \
  --name "CV Processing Function Failures" \
  --resource-group "rg-hr-cv-processing" \
  --scopes "/subscriptions/your-subscription-id/resourceGroups/rg-hr-cv-processing/providers/Microsoft.Web/sites/your-function-app-name" \
  --condition "count static FunctionExecutionUnits > 5" \
  --description "Alert when function has more than 5 failures"
```

### **9.2 Cost Monitoring**
```bash
# Set up cost alert
az consumption budget create \
  --budget-name "CV Processing Budget" \
  --amount 50 \
  --time-grain "Monthly" \
  --time-period start-date="2025-09-01" \
  --resource-group "rg-hr-cv-processing"
```

## **10. Troubleshooting Common Issues**

### **10.1 Deployment Issues**
```bash
# Check deployment status
az functionapp deployment list \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing"

# View deployment logs
az functionapp log deployment show \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing" \
  --deployment-id "latest"
```

### **10.2 Runtime Issues**
```bash
# Check function app logs
az functionapp log tail \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing"

# Check application settings
az functionapp config appsettings list \
  --name "your-function-app-name" \
  --resource-group "rg-hr-cv-processing"
```

### **10.3 Performance Issues**
- Monitor Application Insights for detailed telemetry
- Check Azure OpenAI quota and usage
- Review function timeout settings
- Monitor memory usage and cold starts

## **11. Security Best Practices**

### **11.1 Key Management**
- Store sensitive keys in Azure Key Vault
- Use Managed Identity for Azure resource access
- Rotate API keys regularly
- Implement least privilege access

### **11.2 Network Security**
- Consider VNet integration for production
- Implement IP restrictions if needed
- Use Azure Private Link for OpenAI access
- Enable HTTPS only

## **12. Backup and Disaster Recovery**

### **12.1 Function App Backup**
```bash
# Export function app template
az functionapp config backup create \
  --resource-group "rg-hr-cv-processing" \
  --name "your-function-app-name" \
  --backup-name "cv-processing-backup" \
  --storage-account-url "your-storage-account-url"
```

### **12.2 Configuration Backup**
- Keep `assistants.json` in version control
- Backup Azure OpenAI assistant configurations
- Document all environment variables
- Maintain deployment scripts in Git

---

**Estimated Deployment Time:** 30-45 minutes  
**Monthly Cost Estimate:** $20-50 USD (depending on usage)  
**Next Steps:** After deployment, integrate with Power Automate and test end-to-end workflow

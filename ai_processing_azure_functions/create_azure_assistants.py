#!/usr/bin/env python3
"""
Azure OpenAI Assistants Setup Script
Creates all required AI assistants using Azure OpenAI and manages environment configuration

Usage:
    python create_azure_assistants.py
    python create_azure_assistants.py --update-existing
    python create_azure_assistants.py --delete-all
"""

import os
import json
import sys
import argparse
from typing import Dict, List, Optional
from datetime import datetime
from openai import AzureOpenAI

class AzureAssistantManager:
    """Manages Azure OpenAI assistant creation and configuration"""
    
    def __init__(self):
        self.client = None
        self.config = None
        self.created_assistants = {}
        self.env_file_path = ".env"
        self.local_settings_path = "local.settings.json"
        
    def initialize_client(self) -> bool:
        """Initialize Azure OpenAI client"""
        try:
            # Get Azure OpenAI credentials
            endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://oai-mpr-assistant.openai.azure.com/")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")
            
            if not endpoint:
                print("❌ Error: AZURE_OPENAI_ENDPOINT not found in environment variables")
                print("📝 Please set your Azure OpenAI endpoint:")
                print("   export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
                return False
            
            if not api_key:
                print("❌ Error: AZURE_OPENAI_API_KEY not found in environment variables")
                print("📝 Please set your Azure OpenAI API key:")
                print("   export AZURE_OPENAI_API_KEY='your-azure-openai-api-key'")
                return False
            
            self.client = AzureOpenAI(
                api_key=api_key,
                api_version=api_version,
                azure_endpoint=endpoint
            )
            
            # Test connection by listing models
            try:
                models = self.client.models.list()
                print("✅ Azure OpenAI client initialized successfully")
                print(f"   Endpoint: {endpoint}")
                print(f"   API Version: {api_version}")
                return True
            except Exception as e:
                print(f"❌ Failed to connect to Azure OpenAI: {str(e)}")
                return False
            
        except Exception as e:
            print(f"❌ Failed to initialize Azure OpenAI client: {str(e)}")
            return False
    
    def load_assistant_config(self) -> bool:
        """Load assistant configuration from assistants.json"""
        try:
            # Debug: Check current working directory and file existence
            current_dir = os.getcwd()
            file_path = os.path.join(current_dir, "assistants.json")
            file_exists = os.path.exists("assistants.json")
            file_exists_abs = os.path.exists(file_path)
            
            print(f"🔍 Debug: Current working directory: {current_dir}")
            print(f"🔍 Debug: assistants.json exists (relative): {file_exists}")
            print(f"🔍 Debug: assistants.json exists (absolute): {file_exists_abs}")
            print(f"🔍 Debug: Full file path: {file_path}")
            
            # Try absolute path first
            if file_exists_abs:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            else:
                with open("assistants.json", "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    
            print("✅ Assistant configuration loaded successfully")
            return True
        except FileNotFoundError:
            print("❌ Error: assistants.json not found")
            print("📝 Please ensure assistants.json exists in the current directory")
            # List files in current directory for debugging
            try:
                files = os.listdir(".")
                json_files = [f for f in files if f.endswith('.json')]
                print(f"🔍 Debug: JSON files in current directory: {json_files}")
            except:
                pass
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing assistants.json: {str(e)}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error loading assistants.json: {str(e)}")
            return False
    
    def create_assistant(self, assistant_name: str, assistant_config: Dict) -> Optional[str]:
        """Create a single Azure OpenAI assistant"""
        try:
            print(f"🔄 Creating assistant: {assistant_config['name']}")
            
            # Prepare instructions (handle both string and array formats)
            instructions = assistant_config["instructions"]
            if isinstance(instructions, list):
                instructions = "\n".join(instructions)
            
            # For Azure OpenAI, we'll create assistants with structured output support
            create_params = {
                "name": assistant_config["name"],
                "instructions": instructions,
                "model": assistant_config["model"],
                "temperature": assistant_config.get("temperature", 0.1),
                "top_p": assistant_config.get("top_p", 1.0)
            }
            
            # Add response format for structured output if JSON schema is available
            if "json_schema" in assistant_config:
                create_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": f"{assistant_name.replace('cv_', '').replace('_', '_')}_response",
                        "description": assistant_config["description"],
                        "schema": assistant_config["json_schema"],
                        "strict": True
                    }
                }
            
            assistant = self.client.beta.assistants.create(**create_params)
            
            assistant_id = assistant.id
            self.created_assistants[assistant_name] = {
                "id": assistant_id,
                "name": assistant_config["name"],
                "created_at": datetime.now().isoformat()
            }
            
            print(f"✅ Created {assistant_config['name']}")
            print(f"   Assistant ID: {assistant_id}")
            
            return assistant_id
            
        except Exception as e:
            print(f"❌ Failed to create assistant {assistant_name}: {str(e)}")
            return None
    
    def create_all_assistants(self) -> bool:
        """Create all assistants from configuration"""
        success_count = 0
        total_count = len(self.config["assistants"])
        
        print(f"\n🚀 Creating {total_count} Azure OpenAI assistants...")
        print("=" * 50)
        
        for assistant_name, assistant_config in self.config["assistants"].items():
            assistant_id = self.create_assistant(assistant_name, assistant_config)
            if assistant_id:
                success_count += 1
            print()
        
        print("=" * 50)
        print(f"📊 Summary: {success_count}/{total_count} assistants created successfully")
        
        return success_count == total_count
    
    def update_environment_files(self) -> bool:
        """Update environment configuration files with assistant IDs"""
        try:
            # Generate environment variable mappings
            env_mappings = {
                "cv_data_extractor": "CV_DATA_EXTRACTOR_ASSISTANT_ID",
                "cv_pii_identifier": "CV_PII_IDENTIFIER_ASSISTANT_ID", 
                "cv_skills_analyst": "CV_SKILLS_ANALYST_ASSISTANT_ID"
            }
            
            # Update .env file
            self._update_env_file(env_mappings)
            
            # Update local.settings.json
            self._update_local_settings(env_mappings)
            
            print("✅ Environment files updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update environment files: {str(e)}")
            return False
    
    def _update_env_file(self, env_mappings: Dict[str, str]):
        """Update .env file with assistant IDs and Azure OpenAI settings"""
        env_lines = []
        
        # Read existing .env file if it exists
        if os.path.exists(self.env_file_path):
            with open(self.env_file_path, "r") as f:
                env_lines = f.readlines()
        
        # Track which variables we've updated
        updated_vars = set()
        
        # Update existing lines
        for i, line in enumerate(env_lines):
            # Update assistant IDs
            for assistant_name, env_var in env_mappings.items():
                if line.startswith(f"{env_var}="):
                    if assistant_name in self.created_assistants:
                        env_lines[i] = f"{env_var}={self.created_assistants[assistant_name]['id']}\n"
                        updated_vars.add(env_var)
            
            # Update Azure OpenAI settings if they exist
            azure_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_API_VERSION", "AZURE_OPENAI_DEPLOYMENT_NAME"]
            for var in azure_vars:
                if line.startswith(f"{var}="):
                    updated_vars.add(var)
        
        # Add new assistant ID variables if they don't exist
        for assistant_name, env_var in env_mappings.items():
            if env_var not in updated_vars and assistant_name in self.created_assistants:
                env_lines.append(f"{env_var}={self.created_assistants[assistant_name]['id']}\n")
        
        # Add Azure OpenAI variables if they don't exist
        azure_defaults = {
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "https://oai-mpr-assistant.openai.azure.com/"),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key"),
            "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini-for-cvs")
        }
        
        for var, default_value in azure_defaults.items():
            if var not in updated_vars:
                env_lines.append(f"{var}={default_value}\n")
        
        # Write updated .env file
        with open(self.env_file_path, "w") as f:
            f.writelines(env_lines)
        
        print(f"📝 Updated {self.env_file_path}")
    
    def _update_local_settings(self, env_mappings: Dict[str, str]):
        """Update local.settings.json with assistant IDs and Azure OpenAI settings"""
        local_settings = {
            "IsEncrypted": False,
            "Values": {
                "AzureWebJobsStorage": "UseDevelopmentStorage=true",
                "FUNCTIONS_WORKER_RUNTIME": "python",
                "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT", "https://your-resource.openai.azure.com/"),
                "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key"),
                "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
                "AZURE_OPENAI_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"),
                "PROCESSING_TIMEOUT_SECONDS": "30",
                "MAX_FILE_SIZE_MB": "10",
                "ENABLE_DEBUG_LOGGING": "true"
            }
        }
        
        # Read existing local.settings.json if it exists
        if os.path.exists(self.local_settings_path):
            try:
                with open(self.local_settings_path, "r") as f:
                    existing_settings = json.load(f)
                    local_settings["Values"].update(existing_settings.get("Values", {}))
            except json.JSONDecodeError:
                print("⚠️  Warning: Could not parse existing local.settings.json, creating new one")
        
        # Update assistant IDs
        for assistant_name, env_var in env_mappings.items():
            if assistant_name in self.created_assistants:
                local_settings["Values"][env_var] = self.created_assistants[assistant_name]["id"]
        
        # Write updated local.settings.json
        with open(self.local_settings_path, "w") as f:
            json.dump(local_settings, f, indent=2)
        
        print(f"📝 Updated {self.local_settings_path}")
    
    def save_assistant_summary(self):
        """Save summary of created assistants"""
        summary = {
            "provider": "azure_openai",
            "created_at": datetime.now().isoformat(),
            "total_assistants": len(self.created_assistants),
            "azure_endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview"),
            "assistants": self.created_assistants,
            "environment_variables": {
                "CV_DATA_EXTRACTOR_ASSISTANT_ID": self.created_assistants.get("cv_data_extractor", {}).get("id"),
                "CV_PII_IDENTIFIER_ASSISTANT_ID": self.created_assistants.get("cv_pii_identifier", {}).get("id"),
                "CV_SKILLS_ANALYST_ASSISTANT_ID": self.created_assistants.get("cv_skills_analyst", {}).get("id")
            }
        }
        
        with open("azure_assistant_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("📄 Azure assistant summary saved to azure_assistant_summary.json")
    
    def list_existing_assistants(self) -> List[Dict]:
        """List all existing assistants"""
        try:
            assistants = self.client.beta.assistants.list()
            return assistants.data
        except Exception as e:
            print(f"❌ Failed to list assistants: {str(e)}")
            return []
    
    def delete_assistant(self, assistant_id: str) -> bool:
        """Delete a specific assistant"""
        try:
            self.client.beta.assistants.delete(assistant_id)
            return True
        except Exception as e:
            print(f"❌ Failed to delete assistant {assistant_id}: {str(e)}")
            return False
    
    def delete_all_assistants(self) -> bool:
        """Delete all assistants (use with caution)"""
        print("⚠️  WARNING: This will delete ALL your Azure OpenAI assistants!")
        confirm = input("Type 'DELETE ALL' to confirm: ")
        
        if confirm != "DELETE ALL":
            print("❌ Deletion cancelled")
            return False
        
        assistants = self.list_existing_assistants()
        if not assistants:
            print("ℹ️  No assistants found to delete")
            return True
        
        success_count = 0
        for assistant in assistants:
            if self.delete_assistant(assistant.id):
                print(f"✅ Deleted assistant: {assistant.name} ({assistant.id})")
                success_count += 1
            else:
                print(f"❌ Failed to delete assistant: {assistant.name} ({assistant.id})")
        
        print(f"📊 Deleted {success_count}/{len(assistants)} assistants")
        return success_count == len(assistants)
    
    def print_setup_instructions(self):
        """Print setup instructions after successful creation"""
        print("\n" + "=" * 60)
        print("🎉 AZURE OPENAI ASSISTANTS SETUP COMPLETE!")
        print("=" * 60)
        print("\n📋 Next Steps:")
        print("1. ✅ Assistant IDs have been saved to .env and local.settings.json")
        print("2. 🔄 Restart your development environment to load new variables")
        print("3. 🧪 Test your assistants in Azure OpenAI Studio:")
        print(f"   {os.getenv('AZURE_OPENAI_ENDPOINT', 'https://your-resource.openai.azure.com/')}")
        
        for assistant_name, assistant_info in self.created_assistants.items():
            print(f"   • {assistant_info['name']}: {assistant_info['id']}")
        
        print("\n4. 🚀 Deploy to Azure Functions:")
        print("   func azure functionapp publish your-function-app-name --python")
        
        print("\n5. ⚙️  Set environment variables in Azure:")
        print("   az functionapp config appsettings set \\")
        print("     --name 'your-function-app-name' \\")
        print("     --resource-group 'your-resource-group' \\")
        print("     --settings \\")
        
        azure_vars = [
            ("AZURE_OPENAI_ENDPOINT", os.getenv("AZURE_OPENAI_ENDPOINT")),
            ("AZURE_OPENAI_API_KEY", "your-azure-openai-api-key"),
            ("AZURE_OPENAI_API_VERSION", os.getenv("AZURE_OPENAI_API_VERSION", "2024-05-01-preview")),
            ("AZURE_OPENAI_DEPLOYMENT_NAME", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o-mini"))
        ]
        
        for var_name, var_value in azure_vars:
            print(f"       '{var_name}={var_value}' \\")
        
        for assistant_name, assistant_info in self.created_assistants.items():
            env_var = assistant_name.upper().replace("CV_", "CV_").replace("_", "_") + "_ASSISTANT_ID"
            print(f"       '{env_var}={assistant_info['id']}' \\")
        
        print("\n📊 Cost Estimate:")
        print(f"   • 20 CVs/hour × 30 days = ~$15-40/month with Azure OpenAI GPT-4o-mini")
        print(f"   • Each CV processing: ~$0.01-0.06")
        
        print("\n📁 Files Created/Updated:")
        print("   • .env (environment variables)")
        print("   • local.settings.json (Azure Functions local config)")
        print("   • azure_assistant_summary.json (assistant details)")

def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Azure OpenAI Assistants Setup Script")
    parser.add_argument("--update-existing", action="store_true", 
                       help="Update existing assistants instead of creating new ones")
    parser.add_argument("--delete-all", action="store_true",
                       help="Delete all existing assistants (DANGEROUS)")
    parser.add_argument("--list", action="store_true",
                       help="List all existing assistants")
    
    args = parser.parse_args()
    
    print("🤖 Azure OpenAI Assistants Setup Script")
    print("=" * 45)
    
    # Create assistant manager
    manager = AzureAssistantManager()
    
    # Initialize Azure OpenAI client
    if not manager.initialize_client():
        sys.exit(1)
    
    # Handle different operations
    if args.delete_all:
        manager.delete_all_assistants()
        return
    
    if args.list:
        assistants = manager.list_existing_assistants()
        print(f"\n📋 Found {len(assistants)} existing assistants:")
        for assistant in assistants:
            print(f"   • {assistant.name}: {assistant.id}")
        return
    
    # Load configuration
    if not manager.load_assistant_config():
        sys.exit(1)
    
    # Create assistants
    if manager.create_all_assistants():
        # Update environment files
        manager.update_environment_files()
        
        # Save summary
        manager.save_assistant_summary()
        
        # Print setup instructions
        manager.print_setup_instructions()
    else:
        print("❌ Some assistants failed to create. Check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

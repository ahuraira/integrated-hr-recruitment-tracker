"""
Utils Module for AI-Powered CV Processing Engine

This module provides centralized configuration management, validation utilities,
and common helper functions for the CV processing system.

Version: 1.0
Date: September 23, 2025
"""

import json
import os
import re
import time
import uuid
import hashlib
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pathlib import Path


# Custom Exception Classes
class UtilsError(Exception):
    """Base exception for utils module errors"""
    pass


class ConfigurationError(UtilsError):
    """Raised when configuration is invalid or missing"""
    pass


class ValidationError(UtilsError):
    """Raised when validation fails"""
    pass


class EnvironmentError(UtilsError):
    """Raised when environment variables are missing or invalid"""
    pass


class ConfigurationManager:
    """
    Manages centralized assistant configuration with environment variable support
    and validation capabilities.
    """
    
    def __init__(self, config_file_path: str = "assistants.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file_path (str): Path to assistants.json configuration file
        """
        self.config_file_path = config_file_path
        self.config_data = None
        self.environment_variables = {}
        self._load_configuration()
        
    def _load_configuration(self):
        """
        Load and parse assistants.json configuration file
        """
        try:
            # Load configuration file
            config_path = Path(self.config_file_path)
            if not config_path.is_absolute():
                # Look for config file relative to this module
                module_dir = Path(__file__).parent.parent
                config_path = module_dir / self.config_file_path
            
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            # Validate configuration structure
            self._validate_config_structure()
            
            # Load environment variables
            self._load_environment_variables()
            
            # Substitute environment variables in configuration
            self._substitute_environment_variables()
            
            logging.info(f"Configuration loaded successfully from {config_path}")
            
        except FileNotFoundError:
            raise ConfigurationError(f"Configuration file not found: {self.config_file_path}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in configuration file: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")

    def _validate_config_structure(self):
        """Validate the structure of assistants.json"""
        required_sections = ["version", "assistants", "global_settings"]
        
        for section in required_sections:
            if section not in self.config_data:
                raise ConfigurationError(f"Missing required section: {section}")
        
        # Validate assistant configurations
        required_assistants = ["cv_data_extractor", "cv_pii_identifier", "cv_skills_analyst"]
        
        for assistant_name in required_assistants:
            if assistant_name not in self.config_data["assistants"]:
                raise ConfigurationError(f"Missing required assistant: {assistant_name}")
            
            assistant_config = self.config_data["assistants"][assistant_name]
            required_fields = ["assistant_id", "instructions", "json_schema", "model"]
            
            for field in required_fields:
                if field not in assistant_config:
                    raise ConfigurationError(f"Missing required field '{field}' in {assistant_name}")

    def _load_environment_variables(self):
        """Load and validate required environment variables"""
        self.environment_variables = {
            "CV_DATA_EXTRACTOR_ASSISTANT_ID": os.getenv("CV_DATA_EXTRACTOR_ASSISTANT_ID"),
            "CV_PII_IDENTIFIER_ASSISTANT_ID": os.getenv("CV_PII_IDENTIFIER_ASSISTANT_ID"),
            "CV_SKILLS_ANALYST_ASSISTANT_ID": os.getenv("CV_SKILLS_ANALYST_ASSISTANT_ID"),
            "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY")
        }
        
        # Check for missing required variables
        missing_vars = [key for key, value in self.environment_variables.items() if not value]
        
        if missing_vars:
            raise ConfigurationError(f"Missing required environment variables: {missing_vars}")

    def _substitute_environment_variables(self):
        """Substitute environment variables in configuration using ${VAR_NAME} syntax"""
        config_str = json.dumps(self.config_data)
        
        # Replace environment variable placeholders
        for var_name, var_value in self.environment_variables.items():
            if var_value:
                config_str = config_str.replace(f"${{{var_name}}}", var_value)
        
        # Check for unresolved variables
        unresolved = re.findall(r'\$\{([^}]+)\}', config_str)
        if unresolved:
            logging.warning(f"Unresolved environment variables in configuration: {unresolved}")
        
        self.config_data = json.loads(config_str)
        
    def load_assistant_config(self, assistant_name: str) -> dict:
        """
        Load specific assistant configuration
        
        Args:
            assistant_name (str): Name of assistant (cv_data_extractor, cv_pii_identifier, cv_skills_analyst)
            
        Returns:
            dict: Complete assistant configuration
            
        Raises:
            ConfigurationError: If assistant not found or configuration invalid
        """
        if not self.config_data:
            raise ConfigurationError("Configuration not loaded")
        
        if assistant_name not in self.config_data["assistants"]:
            raise ConfigurationError(f"Assistant not found: {assistant_name}")
        
        assistant_config = self.config_data["assistants"][assistant_name].copy()
        
        # Add global settings
        assistant_config["global_settings"] = self.config_data.get("global_settings", {})
        
        return assistant_config
        
    def get_assistant_prompt(self, assistant_name: str, **kwargs) -> str:
        """
        Get assistant prompt with variable substitution
        
        Args:
            assistant_name (str): Name of assistant
            **kwargs: Variables for prompt interpolation (e.g., job_title, cv_text)
            
        Returns:
            str: Formatted prompt with variables substituted
        """
        assistant_config = self.load_assistant_config(assistant_name)
        prompt_template = assistant_config.get("instructions", "")
        
        try:
            # Format prompt with provided variables
            formatted_prompt = prompt_template.format(**kwargs)
            return formatted_prompt
            
        except KeyError as e:
            missing_var = str(e).strip("'\"")
            raise ConfigurationError(f"Missing required variable '{missing_var}' for prompt formatting")
        except Exception as e:
            raise ConfigurationError(f"Failed to format prompt: {str(e)}")
        
    def get_assistant_schema(self, assistant_name: str) -> dict:
        """
        Get JSON schema for assistant response validation
        
        Args:
            assistant_name (str): Name of assistant
            
        Returns:
            dict: JSON schema for response validation
        """
        assistant_config = self.load_assistant_config(assistant_name)
        return assistant_config.get("json_schema", {})
        
    def get_assistant_settings(self, assistant_name: str) -> dict:
        """
        Get assistant model settings (temperature, max_tokens, etc.)
        
        Args:
            assistant_name (str): Name of assistant
            
        Returns:
            dict: Model configuration settings
        """
        assistant_config = self.load_assistant_config(assistant_name)
        
        model_settings = {
            "model": assistant_config.get("model", "gpt-4o-mini"),
            "temperature": assistant_config.get("temperature", 0.1),
            "max_tokens": assistant_config.get("max_tokens", 2000),
            "top_p": assistant_config.get("top_p", 1.0)
        }
        
        # Merge with global settings
        global_settings = self.config_data.get("global_settings", {})
        model_settings.update({
            "timeout_seconds": global_settings.get("timeout_seconds", 30),
            "max_retries": global_settings.get("max_retries", 3)
        })
        
        return model_settings
        
    def validate_configuration(self) -> dict:
        """
        Validate complete configuration including environment variables
        
        Returns:
            dict: Validation results with any issues found
        """
        validation_results = {
            "is_valid": True,
            "validation_timestamp": time.time(),
            "issues": [],
            "warnings": [],
            "environment_variables": {},
            "assistant_validation": {}
        }
        
        try:
            # Validate environment variables
            for var_name, var_value in self.environment_variables.items():
                validation_results["environment_variables"][var_name] = {
                    "present": bool(var_value),
                    "value_length": len(var_value) if var_value else 0
                }
                
                if not var_value:
                    validation_results["issues"].append(f"Missing environment variable: {var_name}")
                    validation_results["is_valid"] = False
            
            # Validate each assistant configuration
            for assistant_name in ["cv_data_extractor", "cv_pii_identifier", "cv_skills_analyst"]:
                try:
                    assistant_config = self.load_assistant_config(assistant_name)
                    assistant_validation = self._validate_assistant_config(assistant_name, assistant_config)
                    validation_results["assistant_validation"][assistant_name] = assistant_validation
                    
                    if not assistant_validation["is_valid"]:
                        validation_results["is_valid"] = False
                        validation_results["issues"].extend(assistant_validation["issues"])
                        
                except Exception as e:
                    validation_results["issues"].append(f"Failed to validate {assistant_name}: {str(e)}")
                    validation_results["is_valid"] = False
            
            # Validate global settings
            global_settings = self.config_data.get("global_settings", {})
            if not global_settings:
                validation_results["warnings"].append("No global settings defined")
            
        except Exception as e:
            validation_results["issues"].append(f"Configuration validation failed: {str(e)}")
            validation_results["is_valid"] = False
        
        return validation_results

    def _validate_assistant_config(self, assistant_name: str, config: dict) -> dict:
        """Validate individual assistant configuration"""
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ["assistant_id", "instructions", "json_schema", "model"]
        for field in required_fields:
            if field not in config or not config[field]:
                validation["issues"].append(f"{assistant_name}: Missing or empty {field}")
                validation["is_valid"] = False
        
        # Validate assistant_id format
        assistant_id = config.get("assistant_id", "")
        if assistant_id and not assistant_id.startswith("asst_"):
            validation["warnings"].append(f"{assistant_name}: Assistant ID format may be invalid")
        
        # Validate model parameters
        temperature = config.get("temperature")
        if temperature is not None and not (0 <= temperature <= 2):
            validation["issues"].append(f"{assistant_name}: Temperature must be between 0 and 2")
            validation["is_valid"] = False
        
        max_tokens = config.get("max_tokens")
        if max_tokens is not None and not (1 <= max_tokens <= 16384):
            validation["issues"].append(f"{assistant_name}: max_tokens must be between 1 and 16384")
            validation["is_valid"] = False
        
        # Validate JSON schema
        try:
            schema = config.get("json_schema", {})
            if schema:
                # Basic schema validation
                if "type" not in schema:
                    validation["warnings"].append(f"{assistant_name}: JSON schema missing 'type' field")
        except Exception as e:
            validation["issues"].append(f"{assistant_name}: Invalid JSON schema: {str(e)}")
            validation["is_valid"] = False
        
        return validation
        
    def get_global_settings(self) -> dict:
        """Get global system settings from configuration"""
        return self.config_data.get("global_settings", {})
        
    def reload_configuration(self) -> bool:
        """Reload configuration from file (for dynamic updates)"""
        try:
            self._load_configuration()
            return True
        except Exception as e:
            logging.error(f"Failed to reload configuration: {str(e)}")
            return False


class ValidationUtils:
    """Common validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        if not phone:
            return False
        pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        cleaned_phone = re.sub(r'[^\d\+\-\(\)\s]', '', phone)
        return re.match(pattern, cleaned_phone) is not None
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        if not url:
            return False
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = None) -> str:
        """Sanitize and clean text input"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if needed
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rstrip() + "..."
        
        return cleaned
    
    @staticmethod
    def extract_numeric_value(text: str) -> float:
        """Extract numeric value from text (for salary, experience years)"""
        if not text:
            return 0
        
        # Remove commas and extract numeric part
        numeric_match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', str(text))
        if numeric_match:
            return float(numeric_match.group(1).replace(',', ''))
        
        return 0


class TextProcessingUtils:
    """Text processing utilities"""
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 10000, suffix: str = "...") -> str:
        """Truncate text with informative suffix"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def generate_hash(text: str) -> str:
        """Generate MD5 hash for text content"""
        if not text:
            return ""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    @staticmethod
    def extract_file_extension(filename: str) -> str:
        """Extract file extension from filename"""
        if not filename:
            return ""
        return os.path.splitext(filename)[1].lower()
    
    @staticmethod
    def is_valid_file_type(filename: str, allowed_types: list = None) -> bool:
        """Check if file type is allowed"""
        if not filename:
            return False
        if allowed_types is None:
            allowed_types = ['.pdf', '.docx']
        
        ext = TextProcessingUtils.extract_file_extension(filename)
        return ext in allowed_types


class ErrorUtils:
    """Error handling utilities"""
    
    @staticmethod
    def create_error_response(error_type: str, error_message: str, 
                            correlation_id: str = None, details: dict = None) -> dict:
        """Create standardized error response"""
        error_response = {
            "processingStatus": "Failed",
            "errorType": error_type,
            "errorMessage": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if correlation_id:
            error_response["correlationId"] = correlation_id
        
        if details:
            error_response["errorDetails"] = details
        
        return error_response
    
    @staticmethod
    def classify_error(error: Exception) -> str:
        """Classify error type for consistent handling"""
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        if "timeout" in error_message:
            return "TIMEOUT_ERROR"
        elif "rate limit" in error_message:
            return "RATE_LIMIT_ERROR"
        elif "authentication" in error_message:
            return "AUTHENTICATION_ERROR"
        elif "connection" in error_message:
            return "CONNECTION_ERROR"
        elif "validation" in error_message:
            return "VALIDATION_ERROR"
        elif "configuration" in error_message:
            return "CONFIGURATION_ERROR"
        else:
            return "UNKNOWN_ERROR"


class CorrelationUtils:
    """Correlation ID utilities"""
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate unique correlation ID for request tracking"""
        timestamp = int(time.time())
        random_suffix = str(uuid.uuid4())[:8]
        return f"proc_{timestamp}_{random_suffix}"
    
    @staticmethod
    def is_valid_correlation_id(correlation_id: str) -> bool:
        """Validate correlation ID format"""
        if not correlation_id:
            return False
        pattern = r'^proc_\d+_[a-f0-9]{8}$'
        return re.match(pattern, correlation_id) is not None


# Global configuration manager instance
_config_manager = None


def get_config_manager() -> ConfigurationManager:
    """Get singleton configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager


def load_assistant_config(assistant_name: str) -> dict:
    """Load assistant configuration (global function)"""
    return get_config_manager().load_assistant_config(assistant_name)


def get_assistant_prompt(assistant_name: str, **kwargs) -> str:
    """Get formatted assistant prompt (global function)"""
    return get_config_manager().get_assistant_prompt(assistant_name, **kwargs)


def get_assistant_schema(assistant_name: str) -> dict:
    """Get assistant JSON schema (global function)"""
    return get_config_manager().get_assistant_schema(assistant_name)


def get_assistant_settings(assistant_name: str) -> dict:
    """Get assistant model settings (global function)"""
    return get_config_manager().get_assistant_settings(assistant_name)


def validate_system_configuration() -> dict:
    """Validate complete system configuration"""
    return get_config_manager().validate_configuration()


def get_required_environment_variables() -> dict:
    """Get list of required environment variables"""
    return {
        "AZURE_OPENAI_ENDPOINT": "Azure OpenAI service endpoint",
        "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
        "CV_DATA_EXTRACTOR_ASSISTANT_ID": "Assistant ID for candidate data extraction",
        "CV_PII_IDENTIFIER_ASSISTANT_ID": "Assistant ID for PII identification",
        "CV_SKILLS_ANALYST_ASSISTANT_ID": "Assistant ID for skills analysis"
    }


def validate_environment_variables() -> dict:
    """Validate all required environment variables are present"""
    required_vars = get_required_environment_variables()
    validation_result = {
        "all_present": True,
        "missing_variables": [],
        "present_variables": []
    }
    
    for var_name, description in required_vars.items():
        var_value = os.getenv(var_name)
        if var_value:
            validation_result["present_variables"].append(var_name)
        else:
            validation_result["missing_variables"].append(var_name)
            validation_result["all_present"] = False
    
    return validation_result


# Assistant configuration schema for validation
ASSISTANTS_CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "updated_at": {"type": "string"},
        "environment": {"type": "string"},
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
                "timeout_seconds": {"type": "integer"},
                "max_retries": {"type": "integer"},
                "rate_limit_per_minute": {"type": "integer"}
            }
        }
    },
    "required": ["version", "assistants", "global_settings"],
    "definitions": {
        "assistant": {
            "type": "object",
            "properties": {
                "assistant_id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "model": {"type": "string"},
                "temperature": {"type": "number", "minimum": 0, "maximum": 2},
                "top_p": {"type": "number", "minimum": 0, "maximum": 1},
                "max_tokens": {"type": "integer", "minimum": 1, "maximum": 16384},
                "instructions": {"type": "string"},
                "json_schema": {"type": "object"}
            },
            "required": ["assistant_id", "instructions", "json_schema", "model"]
        }
    }
}

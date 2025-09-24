"""
OpenAI Service Module
AI-Powered CV Processing Engine for TTE Recruitment Suite

This module handles interactions with Azure OpenAI assistants for CV processing.
It manages API calls, authentication, and response handling.

Version: 1.0
Date: September 23, 2025
"""

import os
import logging
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OpenAIResponse:
    """Data class for OpenAI API responses"""
    content: str
    usage: Any
    model: str
    finish_reason: str

class OpenAIService:
    """
    Service class for interacting with Azure OpenAI assistants
    """
    
    def __init__(self):
        """Initialize the OpenAI service with Azure configuration"""
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        
        # Assistant IDs
        self.assistant_ids = {
            "CV_DATA_EXTRACTOR": os.getenv("CV_DATA_EXTRACTOR_ASSISTANT_ID"),
            "CV_PII_IDENTIFIER": os.getenv("CV_PII_IDENTIFIER_ASSISTANT_ID"),
            "CV_SKILLS_ANALYST": os.getenv("CV_SKILLS_ANALYST_ASSISTANT_ID")
        }
        
        # Validate configuration
        self._validate_configuration()
        
        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )
        
        logger.info("OpenAI service initialized successfully")
    
    def _validate_configuration(self):
        """Validate that all required configuration is present"""
        if not self.endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is required")
        
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")
        
        for assistant_type, assistant_id in self.assistant_ids.items():
            if not assistant_id:
                raise ValueError(f"{assistant_type}_ASSISTANT_ID environment variable is required")
    
    def get_assistant_id(self, assistant_type: str) -> str:
        """
        Get assistant ID for a specific assistant type
        
        Args:
            assistant_type: Type of assistant (CV_DATA_EXTRACTOR, CV_PII_IDENTIFIER, CV_SKILLS_ANALYST)
            
        Returns:
            Assistant ID string
            
        Raises:
            ValueError: If assistant type is invalid
        """
        if assistant_type not in self.assistant_ids:
            raise ValueError(f"Invalid assistant type: {assistant_type}")
        
        return self.assistant_ids[assistant_type]
    
    def call_assistant(self, assistant_type: str, prompt: str, timeout: int = 30) -> OpenAIResponse:
        """
        Call an Azure OpenAI assistant with the given prompt
        
        Args:
            assistant_type: Type of assistant to call
            prompt: Input prompt for the assistant
            timeout: Request timeout in seconds
            
        Returns:
            OpenAIResponse object with the response data
            
        Raises:
            Exception: If the API call fails
        """
        assistant_id = self.get_assistant_id(assistant_type)
        
        logger.info(f"Calling {assistant_type} assistant (ID: {assistant_id})")
        
        try:
            # Create a thread
            thread = self.client.beta.threads.create()
            
            # Add the user message to the thread
            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )
            
            # Run the assistant
            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id
            )
            
            # Poll for completion
            while run.status in ['queued', 'in_progress', 'cancelling']:
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
            
            if run.status == 'completed':
                # Retrieve the messages
                messages = self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                # Get the assistant's response (latest message)
                assistant_message = messages.data[0]
                response_content = assistant_message.content[0].text.value
                
                # Create response object
                response = OpenAIResponse(
                    content=response_content,
                    usage=run.usage,
                    model=run.model,
                    finish_reason=run.status
                )
                
                logger.info(f"Assistant call completed successfully. Tokens used: {run.usage.total_tokens if run.usage else 'N/A'}")
                return response
                
            elif run.status == 'failed':
                error_msg = f"Assistant run failed: {run.last_error.message if run.last_error else 'Unknown error'}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            elif run.status == 'cancelled':
                error_msg = "Assistant run was cancelled"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            elif run.status == 'expired':
                error_msg = "Assistant run expired"
                logger.error(error_msg)
                raise Exception(error_msg)
                
            else:
                error_msg = f"Assistant run ended with unexpected status: {run.status}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error calling {assistant_type} assistant: {str(e)}")
            raise Exception(f"Failed to call {assistant_type} assistant: {str(e)}")
    
    def call_chat_completion(self, messages: list, model: str = "gpt-4o-mini", temperature: float = 0.3) -> OpenAIResponse:
        """
        Call Azure OpenAI chat completion API directly (alternative to assistants)
        
        Args:
            messages: List of message objects
            model: Model name to use
            temperature: Temperature setting for response randomness
            
        Returns:
            OpenAIResponse object with the response data
        """
        logger.info(f"Calling chat completion with model: {model}")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=4000
            )
            
            # Create response object
            openai_response = OpenAIResponse(
                content=response.choices[0].message.content,
                usage=response.usage,
                model=response.model,
                finish_reason=response.choices[0].finish_reason
            )
            
            logger.info(f"Chat completion successful. Tokens used: {response.usage.total_tokens}")
            return openai_response
            
        except Exception as e:
            logger.error(f"Error in chat completion: {str(e)}")
            raise Exception(f"Chat completion failed: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to Azure OpenAI service
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to list models as a simple connectivity test
            models = self.client.models.list()
            logger.info("Azure OpenAI connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Azure OpenAI connection test failed: {str(e)}")
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model information dictionary or None if not found
        """
        try:
            model = self.client.models.retrieve(model_name)
            return {
                "id": model.id,
                "created": model.created,
                "owned_by": model.owned_by
            }
            
        except Exception as e:
            logger.warning(f"Could not retrieve model info for {model_name}: {str(e)}")
            return None

"""
OpenAI Service Module
AI-Powered CV Processing Engine for TTE Recruitment Suite

This module handles interactions with Azure OpenAI assistants for CV processing.
It manages API calls, authentication, and response handling.

Version: 1.0
Date: September 23, 2025
"""

import os
import time
import logging
from typing import Dict, Any, Optional
from openai import AzureOpenAI
from dataclasses import dataclass

TERMINAL_RUN_STATUSES = {"completed", "failed", "cancelled", "expired", "incomplete"}
POLL_INITIAL_INTERVAL = 1.0
POLL_MAX_INTERVAL = 5.0
POLL_BACKOFF_FACTOR = 1.5
RUN_EXPIRES_AFTER_SECONDS = 600

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
    
    def call_assistant(self, assistant_type: str, prompt: str, timeout: int = 300) -> OpenAIResponse:
        """
        Call an Azure OpenAI assistant with the given prompt.

        Args:
            assistant_type: Type of assistant to call
            prompt: Input prompt for the assistant
            timeout: Wall-clock timeout in seconds for the whole run (poll + generate).
                     The assistant run is created with expires_after=RUN_EXPIRES_AFTER_SECONDS
                     so a stuck queued run self-expires server-side as well.

        Returns:
            OpenAIResponse object with the response data

        Raises:
            TimeoutError: If the run does not reach a terminal state within `timeout`.
            Exception: If the API call fails.
        """
        assistant_id = self.get_assistant_id(assistant_type)

        logger.info(f"Calling {assistant_type} assistant (ID: {assistant_id})")

        thread = None
        try:
            thread = self.client.beta.threads.create()

            self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=prompt
            )

            run = self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=assistant_id,
                expires_after={"anchor": "last_active_at", "seconds": RUN_EXPIRES_AFTER_SECONDS},
            )

            deadline = time.monotonic() + timeout
            interval = POLL_INITIAL_INTERVAL
            poll_count = 0
            while run.status not in TERMINAL_RUN_STATUSES:
                if time.monotonic() >= deadline:
                    logger.error(
                        f"Client-side timeout after {timeout}s waiting for run {run.id} "
                        f"(last status={run.status}). Attempting cancel."
                    )
                    try:
                        self.client.beta.threads.runs.cancel(thread_id=thread.id, run_id=run.id)
                    except Exception as cancel_err:
                        logger.warning(f"Cancel attempt failed: {cancel_err}")
                    raise TimeoutError(
                        f"Assistant run {run.id} did not complete within {timeout}s "
                        f"(last status={run.status})"
                    )

                time.sleep(interval)
                interval = min(interval * POLL_BACKOFF_FACTOR, POLL_MAX_INTERVAL)
                poll_count += 1

                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )

            logger.info(
                f"Run {run.id} reached terminal status '{run.status}' after {poll_count} polls"
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
                error_msg = (
                    f"Assistant run {run.id} expired without starting "
                    f"(started_at={getattr(run, 'started_at', None)}, "
                    f"usage={getattr(run, 'usage', None)}). "
                    "Common causes: (1) the underlying model deployment has been retired "
                    "or is unavailable, (2) TPM quota exhausted, (3) a stuck prior run on "
                    "the same thread. Check the deployment's model version and Azure OpenAI "
                    "quotas."
                )
                logger.error(error_msg)
                raise Exception(error_msg)

            elif run.status == 'incomplete':
                details = getattr(run, 'incomplete_details', None)
                
                # Check if it's a content filter issue
                if details and hasattr(details, 'reason'):
                    if details.reason == 'content_filter':
                        error_msg = (
                            f"Assistant run blocked by Azure content filter. "
                            f"This usually means the CV content or prompt contains text flagged as potentially "
                            f"inappropriate by Azure's safety systems. "
                            f"Details: {details}. "
                            f"Try: 1) Review CV for any flagged content, 2) Check assistant instructions, "
                            f"3) Contact Azure support to review content filter settings."
                        )
                    elif details.reason == 'max_completion_tokens':
                        error_msg = f"Assistant run incomplete - exceeded max completion tokens. Details: {details}"
                    elif details.reason == 'max_prompt_tokens':
                        error_msg = f"Assistant run incomplete - exceeded max prompt tokens. Details: {details}"
                    else:
                        error_msg = f"Assistant run incomplete. Reason: {details.reason}. Details: {details}"
                else:
                    error_msg = f"Assistant run incomplete. Details: {details if details else 'No details available'}"
                
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

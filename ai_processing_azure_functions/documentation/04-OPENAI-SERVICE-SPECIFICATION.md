# OpenAI Service Module Specification

**Module:** `shared_code/openai_service.py`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Module Overview**

The OpenAI Service module provides a robust, enterprise-grade interface to Azure OpenAI services. It handles all AI assistant interactions with comprehensive error handling, retry logic, rate limiting, and performance monitoring. This module abstracts the complexity of Azure OpenAI API calls and provides a clean interface for the candidate data service.

### **Core Responsibilities:**
- Azure OpenAI client configuration and management
- AI assistant API calls with structured JSON responses
- Retry logic with exponential backoff for reliability
- Rate limiting for cost control (GPT-4o-mini optimization)
- Token usage tracking and cost estimation
- Response validation and JSON schema compliance
- Comprehensive error handling and timeout management

## **2. Functional Requirements**

### **2.1 Azure OpenAI Integration**
- **Client Management:** Initialize and manage Azure OpenAI client connections
- **Assistant API Calls:** Execute calls to pre-configured AI assistants
- **Authentication:** Handle API key authentication securely
- **Endpoint Management:** Support configurable Azure OpenAI endpoints

### **2.2 Reliability Features**
- **Retry Logic:** Exponential backoff for transient failures
- **Timeout Handling:** Configurable timeouts for all API calls
- **Rate Limiting:** Lean rate limiting for cost optimization
- **Circuit Breaker:** Prevent cascading failures during outages

### **2.3 Response Processing**
- **JSON Validation:** Ensure responses match expected schemas
- **Token Tracking:** Monitor input/output token usage
- **Cost Estimation:** Calculate API call costs
- **Response Sanitization:** Clean and validate AI responses

### **2.4 Performance Monitoring**
- **Call Duration Tracking:** Monitor API call performance
- **Success Rate Metrics:** Track call success/failure rates
- **Token Usage Analytics:** Analyze token consumption patterns
- **Error Classification:** Categorize and track error types

## **3. Technical Specifications**

### **3.1 Class Structure**
```python
class OpenAIService:
    """
    Enterprise-grade Azure OpenAI service with comprehensive error handling,
    retry logic, and performance monitoring.
    """
    
    def __init__(self, ai_logger=None):
        """
        Initialize OpenAI service with configuration
        
        Args:
            ai_logger: AI call logger instance for comprehensive logging
        """
        self.client = None
        self.ai_logger = ai_logger
        self.rate_limiter = RateLimiter()
        self.circuit_breaker = CircuitBreaker()
        self.token_tracker = TokenTracker()
        self._initialize_client()
        
    def call_assistant(self, assistant_id: str, prompt: str, expected_json_schema: str = None) -> dict:
        """
        Main entry point for AI assistant calls
        
        Args:
            assistant_id (str): Azure OpenAI assistant ID
            prompt (str): Input prompt for the assistant
            expected_json_schema (str): Expected response schema name
            
        Returns:
            dict: Parsed AI response
            
        Raises:
            OpenAIServiceError: For various API call failures
        """
        
    def _initialize_client(self):
        """Initialize Azure OpenAI client with configuration"""
        
    def _execute_assistant_call(self, assistant_id: str, prompt: str) -> dict:
        """Execute assistant call with retry logic"""
        
    def _validate_response(self, response: dict, expected_schema: str) -> bool:
        """Validate AI response against expected JSON schema"""
        
    def _parse_json_response(self, response_text: str) -> dict:
        """Parse and validate JSON response from AI"""
        
    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate estimated cost for API call"""
        
    def _handle_api_error(self, error: Exception, context: dict) -> dict:
        """Handle and categorize API errors"""
        
    def get_service_health(self) -> dict:
        """Get current service health and performance metrics"""
```

### **3.2 Rate Limiting Implementation**
```python
class RateLimiter:
    """
    Lean rate limiter for GPT-4o-mini cost optimization
    """
    
    def __init__(self):
        self.requests_per_minute = 20  # Conservative limit for cost control
        self.request_times = []
        self.lock = threading.Lock()
        
    def acquire(self) -> bool:
        """
        Acquire rate limit permission
        
        Returns:
            bool: True if request can proceed, False if rate limited
        """
        with self.lock:
            now = time.time()
            
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            
            # Check if we can make another request
            if len(self.request_times) < self.requests_per_minute:
                self.request_times.append(now)
                return True
            
            return False
    
    def get_wait_time(self) -> float:
        """Get recommended wait time before next request"""
        if not self.request_times:
            return 0
        
        oldest_request = min(self.request_times)
        return max(0, 60 - (time.time() - oldest_request))
```

### **3.3 Circuit Breaker Pattern**
```python
class CircuitBreaker:
    """
    Circuit breaker to prevent cascading failures
    """
    
    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        
    def can_proceed(self) -> bool:
        """Check if requests can proceed through circuit breaker"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """Record successful API call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """Record failed API call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
```

### **3.4 Retry Logic with Exponential Backoff**
```python
def _execute_with_retry(self, func, *args, max_retries: int = 3, **kwargs) -> dict:
    """
    Execute function with exponential backoff retry logic
    
    Args:
        func: Function to execute
        max_retries: Maximum number of retry attempts
        
    Returns:
        dict: Function result
        
    Raises:
        OpenAIServiceError: After all retries exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            # Check circuit breaker
            if not self.circuit_breaker.can_proceed():
                raise OpenAIServiceError("Circuit breaker is OPEN - service unavailable")
            
            # Check rate limit
            if not self.rate_limiter.acquire():
                wait_time = self.rate_limiter.get_wait_time()
                if attempt < max_retries:
                    time.sleep(wait_time)
                    continue
                else:
                    raise OpenAIServiceError("Rate limit exceeded")
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Record success
            self.circuit_breaker.record_success()
            return result
            
        except (openai.APITimeoutError, openai.APIConnectionError) as e:
            last_exception = e
            self.circuit_breaker.record_failure()
            
            if attempt < max_retries:
                # Exponential backoff: 1s, 2s, 4s
                wait_time = 2 ** attempt
                logging.warning(f"API call failed (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                raise OpenAIServiceError(f"API call failed after {max_retries} retries: {str(e)}")
                
        except (openai.AuthenticationError, openai.PermissionDeniedError) as e:
            # Don't retry authentication errors
            self.circuit_breaker.record_failure()
            raise OpenAIServiceError(f"Authentication error: {str(e)}")
            
        except Exception as e:
            last_exception = e
            self.circuit_breaker.record_failure()
            
            if attempt < max_retries:
                wait_time = 2 ** attempt
                logging.error(f"Unexpected error (attempt {attempt + 1}), retrying in {wait_time}s: {str(e)}")
                time.sleep(wait_time)
            else:
                raise OpenAIServiceError(f"Unexpected error after {max_retries} retries: {str(e)}")
    
    raise OpenAIServiceError(f"All retry attempts failed. Last error: {str(last_exception)}")
```

## **4. AI Assistant Call Implementation**

### **4.1 Main Assistant Call Method**
```python
def call_assistant(self, assistant_id: str, prompt: str, expected_json_schema: str = None) -> dict:
    """
    Execute AI assistant call with comprehensive error handling
    
    Args:
        assistant_id: Azure OpenAI assistant ID
        prompt: Input prompt text
        expected_json_schema: Expected response schema for validation
        
    Returns:
        dict: Parsed and validated AI response
    """
    call_start_time = time.time()
    correlation_id = str(uuid.uuid4())
    
    try:
        # Log call initiation
        if self.ai_logger:
            self.ai_logger.log_call_start(
                correlation_id=correlation_id,
                assistant_id=assistant_id,
                prompt_length=len(prompt)
            )
        
        # Execute call with retry logic
        response_data = self._execute_with_retry(
            self._make_assistant_call,
            assistant_id,
            prompt
        )
        
        # Parse and validate response
        parsed_response = self._parse_json_response(response_data["response_text"])
        
        if expected_json_schema:
            is_valid = self._validate_response(parsed_response, expected_json_schema)
            if not is_valid:
                raise OpenAIServiceError(f"Response validation failed for schema: {expected_json_schema}")
        
        # Calculate metrics
        call_duration = (time.time() - call_start_time) * 1000
        estimated_cost = self._calculate_cost(
            response_data["input_tokens"],
            response_data["output_tokens"],
            "gpt-4o-mini"
        )
        
        # Log successful call
        if self.ai_logger:
            self.ai_logger.log_call_success(
                correlation_id=correlation_id,
                assistant_id=assistant_id,
                input_tokens=response_data["input_tokens"],
                output_tokens=response_data["output_tokens"],
                call_duration_ms=call_duration,
                estimated_cost=estimated_cost
            )
        
        return parsed_response
        
    except Exception as e:
        call_duration = (time.time() - call_start_time) * 1000
        
        # Log failed call
        if self.ai_logger:
            self.ai_logger.log_call_failure(
                correlation_id=correlation_id,
                assistant_id=assistant_id,
                error_message=str(e),
                call_duration_ms=call_duration
            )
        
        raise e

def _make_assistant_call(self, assistant_id: str, prompt: str) -> dict:
    """
    Make actual API call to Azure OpenAI assistant
    
    Returns:
        dict: Raw response data with token counts
    """
    try:
        # Create thread
        thread = self.client.beta.threads.create()
        
        # Add message to thread
        self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        
        # Run assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for completion with timeout
        timeout_seconds = 30
        start_time = time.time()
        
        while run.status in ["queued", "in_progress"]:
            if time.time() - start_time > timeout_seconds:
                raise OpenAIServiceError("Assistant call timed out")
            
            time.sleep(1)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
        
        if run.status != "completed":
            raise OpenAIServiceError(f"Assistant run failed with status: {run.status}")
        
        # Get response messages
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        assistant_messages = [msg for msg in messages.data if msg.role == "assistant"]
        
        if not assistant_messages:
            raise OpenAIServiceError("No response from assistant")
        
        response_text = assistant_messages[0].content[0].text.value
        
        # Extract token usage (if available)
        input_tokens = getattr(run.usage, 'prompt_tokens', 0) if run.usage else 0
        output_tokens = getattr(run.usage, 'completion_tokens', 0) if run.usage else 0
        
        return {
            "response_text": response_text,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "run_id": run.id,
            "thread_id": thread.id
        }
        
    except Exception as e:
        raise OpenAIServiceError(f"Assistant API call failed: {str(e)}")
```

### **4.2 Response Validation and Parsing**
```python
def _parse_json_response(self, response_text: str) -> dict:
    """
    Parse JSON response from AI assistant with error handling
    
    Args:
        response_text: Raw response text from assistant
        
    Returns:
        dict: Parsed JSON object
    """
    try:
        # Try to find JSON content in response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            # Assume entire response is JSON
            json_str = response_text.strip()
        
        # Parse JSON
        parsed_json = json.loads(json_str)
        return parsed_json
        
    except json.JSONDecodeError as e:
        logging.error(f"Failed to parse JSON response: {str(e)}")
        logging.error(f"Raw response: {response_text[:500]}...")
        raise OpenAIServiceError(f"Invalid JSON response from assistant: {str(e)}")

def _validate_response(self, response: dict, expected_schema: str) -> bool:
    """
    Validate response against expected JSON schema
    
    Args:
        response: Parsed JSON response
        expected_schema: Schema name to validate against
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Get schema definition
        schema = self._get_json_schema(expected_schema)
        
        # Validate using jsonschema library
        jsonschema.validate(instance=response, schema=schema)
        return True
        
    except jsonschema.ValidationError as e:
        logging.warning(f"Response validation failed: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Schema validation error: {str(e)}")
        return False

def _get_json_schema(self, schema_name: str) -> dict:
    """Get JSON schema definition by name"""
    schemas = {
        "candidate_profile_schema": {
            "type": "object",
            "properties": {
                "candidateProfile": {
                    "type": "object",
                    "properties": {
                        "candidateName": {"type": ["string", "null"]},
                        "jobTitle": {"type": ["string", "null"]},
                        "candidateEmail": {"type": ["string", "null"]},
                        "candidatePhone": {"type": ["string", "null"]},
                        "totalExperienceYears": {"type": ["number", "null"]},
                        # ... all 18 required fields
                    }
                }
            },
            "required": ["candidateProfile"]
        },
        "pii_entities_schema": {
            "type": "object",
            "properties": {
                "pii_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_value": {"type": "string"},
                            "pii_type": {"type": "string"},
                            "sensitivity_level": {"type": "integer"},
                            "all_variations": {"type": "array"},
                            "context": {"type": "string"}
                        },
                        "required": ["original_value", "pii_type", "sensitivity_level"]
                    }
                }
            },
            "required": ["pii_entities"]
        },
        "skills_analysis_schema": {
            "type": "object",
            "properties": {
                "analysisMetrics": {"type": "object"},
                "professionalProfile": {"type": "object"}
            },
            "required": ["analysisMetrics", "professionalProfile"]
        }
    }
    
    return schemas.get(schema_name, {})
```

## **5. Token Tracking and Cost Estimation**

### **5.1 Token Tracker Implementation**
```python
class TokenTracker:
    """Track token usage and costs across all AI calls"""
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_cost = 0.0
        self.call_count = 0
        self.lock = threading.Lock()
        
    def record_usage(self, input_tokens: int, output_tokens: int, cost: float):
        """Record token usage for a call"""
        with self.lock:
            self.total_input_tokens += input_tokens
            self.total_output_tokens += output_tokens
            self.total_cost += cost
            self.call_count += 1
    
    def get_usage_summary(self) -> dict:
        """Get current usage summary"""
        with self.lock:
            return {
                "total_input_tokens": self.total_input_tokens,
                "total_output_tokens": self.total_output_tokens,
                "total_tokens": self.total_input_tokens + self.total_output_tokens,
                "total_cost": round(self.total_cost, 4),
                "call_count": self.call_count,
                "average_cost_per_call": round(self.total_cost / max(1, self.call_count), 4)
            }

def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Calculate estimated cost for API call
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (e.g., "gpt-4o-mini")
        
    Returns:
        float: Estimated cost in USD
    """
    # GPT-4o-mini pricing (as of Sept 2025)
    pricing = {
        "gpt-4o-mini": {
            "input_per_1k": 0.00015,   # $0.15 per 1K input tokens
            "output_per_1k": 0.0006    # $0.6 per 1K output tokens
        },
        "gpt-4": {
            "input_per_1k": 0.03,     # $30 per 1K input tokens
            "output_per_1k": 0.06     # $60 per 1K output tokens
        }
    }
    
    model_pricing = pricing.get(model, pricing["gpt-4o-mini"])
    
    input_cost = (input_tokens / 1000) * model_pricing["input_per_1k"]
    output_cost = (output_tokens / 1000) * model_pricing["output_per_1k"]
    
    total_cost = input_cost + output_cost
    
    # Record usage
    self.token_tracker.record_usage(input_tokens, output_tokens, total_cost)
    
    return total_cost
```

## **6. Error Handling and Exception Classes**

### **6.1 Custom Exception Hierarchy**
```python
class OpenAIServiceError(Exception):
    """Base exception for OpenAI service errors"""
    pass

class AuthenticationError(OpenAIServiceError):
    """Raised when API authentication fails"""
    pass

class RateLimitError(OpenAIServiceError):
    """Raised when rate limits are exceeded"""
    pass

class ValidationError(OpenAIServiceError):
    """Raised when response validation fails"""
    pass

class TimeoutError(OpenAIServiceError):
    """Raised when API calls timeout"""
    pass

class CircuitBreakerError(OpenAIServiceError):
    """Raised when circuit breaker is open"""
    pass
```

### **6.2 Error Classification and Handling**
```python
def _handle_api_error(self, error: Exception, context: dict) -> dict:
    """
    Classify and handle API errors
    
    Args:
        error: The exception that occurred
        context: Call context for debugging
        
    Returns:
        dict: Error classification and recovery info
    """
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "is_retryable": False,
        "recovery_action": "none",
        "context": context
    }
    
    if isinstance(error, openai.APITimeoutError):
        error_info.update({
            "is_retryable": True,
            "recovery_action": "retry_with_backoff",
            "classification": "timeout"
        })
    elif isinstance(error, openai.RateLimitError):
        error_info.update({
            "is_retryable": True,
            "recovery_action": "wait_and_retry",
            "classification": "rate_limit"
        })
    elif isinstance(error, openai.AuthenticationError):
        error_info.update({
            "is_retryable": False,
            "recovery_action": "check_credentials",
            "classification": "authentication"
        })
    elif isinstance(error, openai.APIConnectionError):
        error_info.update({
            "is_retryable": True,
            "recovery_action": "retry_with_backoff",
            "classification": "connection"
        })
    else:
        error_info.update({
            "is_retryable": False,
            "recovery_action": "manual_investigation",
            "classification": "unknown"
        })
    
    return error_info
```

## **7. Configuration and Initialization**

### **7.1 Client Initialization**
```python
def _initialize_client(self):
    """
    Initialize Azure OpenAI client with configuration validation
    """
    try:
        # Validate required environment variables
        required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise OpenAIServiceError(f"Missing required environment variables: {missing_vars}")
        
        # Initialize client
        self.client = openai.AzureOpenAI(
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-05-01-preview"  # Latest API version
        )
        
        # Test connection
        self._test_connection()
        
        logging.info("Azure OpenAI client initialized successfully")
        
    except Exception as e:
        logging.error(f"Failed to initialize Azure OpenAI client: {str(e)}")
        raise OpenAIServiceError(f"Client initialization failed: {str(e)}")

def _test_connection(self):
    """Test Azure OpenAI connection"""
    try:
        # Simple test call to verify connectivity
        self.client.models.list()
        logging.info("Azure OpenAI connection test successful")
    except Exception as e:
        raise OpenAIServiceError(f"Connection test failed: {str(e)}")
```

### **7.2 Service Configuration**
```python
# Service configuration constants
SERVICE_CONFIG = {
    "max_retries": 3,
    "base_timeout": 30,
    "rate_limit_per_minute": 20,
    "circuit_breaker_threshold": 5,
    "circuit_breaker_timeout": 60,
    "max_prompt_length": 50000,
    "max_response_length": 10000
}

# Model configuration
MODEL_CONFIG = {
    "gpt-4o-mini": {
        "max_tokens": 16384,
        "temperature": 0.1,
        "top_p": 1.0
    }
}
```

## **8. Health Monitoring and Diagnostics**

### **8.1 Service Health Check**
```python
def get_service_health(self) -> dict:
    """
    Get comprehensive service health status
    
    Returns:
        dict: Service health metrics and status
    """
    health_status = {
        "service_status": "healthy",
        "last_health_check": time.time(),
        "circuit_breaker_state": self.circuit_breaker.state,
        "rate_limit_status": {
            "requests_remaining": self.rate_limiter.requests_per_minute - len(self.rate_limiter.request_times),
            "reset_time": self.rate_limiter.get_wait_time()
        },
        "token_usage": self.token_tracker.get_usage_summary(),
        "connection_status": "connected" if self.client else "disconnected"
    }
    
    # Determine overall health
    if self.circuit_breaker.state == "OPEN":
        health_status["service_status"] = "degraded"
    
    return health_status
```

## **9. Integration Requirements**

### **9.1 Dependencies**
```txt
openai>=1.12.0              # Azure OpenAI SDK
jsonschema>=4.17.0          # JSON schema validation
tenacity>=8.2.0             # Retry logic (alternative)
```

### **9.2 Environment Variables**
```python
REQUIRED_ENV_VARS = {
    "AZURE_OPENAI_ENDPOINT": "Azure OpenAI service endpoint URL",
    "AZURE_OPENAI_API_KEY": "Azure OpenAI API key",
    "CV_DATA_EXTRACTOR_ASSISTANT_ID": "Assistant ID for candidate data extraction",
    "CV_PII_IDENTIFIER_ASSISTANT_ID": "Assistant ID for PII identification",
    "CV_SKILLS_ANALYST_ASSISTANT_ID": "Assistant ID for skills analysis"
}
```

### **9.3 Integration Points**
- **Called by:** `CandidateDataService` for all AI assistant interactions
- **Depends on:** `AICallLogger` for comprehensive call logging
- **Provides:** Robust, monitored access to Azure OpenAI assistants
- **Error Handling:** Structured error responses for upstream error handling

---

**Next Steps:**
- Implement OpenAIService class with all reliability features
- Add comprehensive error handling and retry logic
- Integrate with AI call logger for full audit trail
- Configure rate limiting and circuit breaker patterns
- Add comprehensive monitoring and health checks
- Create unit tests for all error scenarios and retry logic

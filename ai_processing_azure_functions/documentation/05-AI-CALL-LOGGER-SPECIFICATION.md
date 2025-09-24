# AI Call Logger Module Specification

**Module:** `shared_code/ai_call_logger.py`  
**Version:** 1.0  
**Date:** September 23, 2025  
**Project:** AI-Powered CV Processing Engine

## **1. Module Overview**

The AI Call Logger module provides comprehensive logging, tracking, and auditing capabilities for all AI assistant interactions. It maintains detailed records of every AI call with complete input/output capture, performance metrics, and error tracking. This module is essential for debugging, auditing, cost analysis, and potential re-execution of AI processing stages.

### **Core Responsibilities:**
- Comprehensive AI call logging with full input/output capture
- Performance metrics tracking (timing, tokens, costs)
- Error logging and failure analysis
- Correlation ID management for request tracing
- Processing status tracking and updates
- Audit trail maintenance for compliance
- Cost analysis and token usage reporting

## **2. Functional Requirements**

### **2.1 Call Logging**
- **Complete Input Capture:** Log full prompts sent to AI assistants
- **Complete Output Capture:** Log full responses received from AI assistants
- **Metadata Logging:** Track timestamps, duration, token counts, model information
- **Correlation Tracking:** Maintain correlation IDs across related calls within processing sessions

### **2.2 Performance Monitoring**
- **Timing Metrics:** Track call duration, queue time, processing time
- **Token Usage:** Monitor input/output tokens for cost analysis
- **Success Rates:** Track success/failure rates per assistant and stage
- **Performance Trends:** Analyze call performance over time

### **2.3 Error Tracking**
- **Failure Documentation:** Log all AI call failures with detailed error information
- **Recovery Tracking:** Track retry attempts and recovery actions
- **Error Classification:** Categorize errors for pattern analysis
- **Debug Information:** Capture context for troubleshooting

### **2.4 Audit and Compliance**
- **Processing History:** Maintain complete audit trail of all AI interactions
- **Data Lineage:** Track data flow through AI processing stages
- **Re-execution Support:** Provide sufficient data to replay AI calls
- **Compliance Reporting:** Generate reports for audit purposes

## **3. Technical Specifications**

### **3.1 Class Structure**
```python
class AICallLogger:
    """
    Comprehensive AI call logging and monitoring system with audit trail capabilities.
    """
    
    def __init__(self):
        """Initialize logger with configuration"""
        self.correlation_id = None
        self.session_logs = []
        self.call_counter = 0
        self.session_start_time = None
        self._initialize_logger()
        
    def start_processing_session(self, file_name: str, job_title: str) -> str:
        """
        Start a new processing session with correlation tracking
        
        Args:
            file_name (str): Name of CV file being processed
            job_title (str): Target job title
            
        Returns:
            str: Generated correlation ID for the session
        """
        
    def log_ai_call(self, stage: str, assistant_id: str, input_prompt: str, 
                   response: dict, call_duration_ms: float = None) -> str:
        """
        Log a successful AI assistant call
        
        Args:
            stage (str): Processing stage (candidate_data_extraction, pii_identification, skills_analysis)
            assistant_id (str): Azure OpenAI assistant ID
            input_prompt (str): Complete input prompt sent to assistant
            response (dict): Complete response from assistant
            call_duration_ms (float): Call duration in milliseconds
            
        Returns:
            str: Call log ID for reference
        """
        
    def log_ai_call_error(self, stage: str, assistant_id: str, error_message: str, 
                         input_prompt: str = None, call_duration_ms: float = None) -> str:
        """
        Log a failed AI assistant call
        
        Args:
            stage (str): Processing stage where error occurred
            assistant_id (str): Azure OpenAI assistant ID (if available)
            error_message (str): Error description
            input_prompt (str): Input prompt that caused error (if available)
            call_duration_ms (float): Call duration before failure
            
        Returns:
            str: Error log ID for reference
        """
        
    def log_processing_status(self, status: str, details: dict = None):
        """Update processing status for current session"""
        
    def get_session_summary(self) -> dict:
        """Get comprehensive summary of current processing session"""
        
    def get_call_logs(self, correlation_id: str = None) -> list:
        """Retrieve call logs for session or specific correlation ID"""
        
    def log_performance_metrics(self, metrics: dict):
        """Log performance metrics for analysis"""
        
    def generate_audit_report(self, correlation_id: str) -> dict:
        """Generate comprehensive audit report for a processing session"""
        
    def export_logs_for_replay(self, correlation_id: str) -> dict:
        """Export logs in format suitable for replay/re-execution"""
```

### **3.2 Log Entry Structure**
```python
class AICallLogEntry:
    """Structure for individual AI call log entries"""
    
    def __init__(self):
        self.call_id = str(uuid.uuid4())
        self.correlation_id = None
        self.timestamp = time.time()
        self.stage = None
        self.assistant_id = None
        self.model_used = "gpt-4o-mini"
        self.success = False
        self.call_duration_ms = 0
        self.input_data = {}
        self.output_data = {}
        self.error_details = None
        self.performance_metrics = {}
        
    def to_dict(self) -> dict:
        """Convert log entry to dictionary for JSON serialization"""
        return {
            "call_id": self.call_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "formatted_timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "stage": self.stage,
            "assistant_id": self.assistant_id,
            "model_used": self.model_used,
            "success": self.success,
            "call_duration_ms": self.call_duration_ms,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error_details": self.error_details,
            "performance_metrics": self.performance_metrics
        }

class ProcessingSession:
    """Structure for processing session metadata"""
    
    def __init__(self, file_name: str, job_title: str):
        self.correlation_id = f"proc_{int(time.time())}_{str(uuid.uuid4())[:8]}"
        self.file_name = file_name
        self.job_title = job_title
        self.start_time = time.time()
        self.end_time = None
        self.status = "in_progress"
        self.call_logs = []
        self.performance_summary = {}
        self.error_count = 0
        self.success_count = 0
```

### **3.3 Logging Implementation**
```python
def log_ai_call(self, stage: str, assistant_id: str, input_prompt: str, 
               response: dict, call_duration_ms: float = None) -> str:
    """
    Log successful AI assistant call with complete details
    """
    call_entry = AICallLogEntry()
    call_entry.correlation_id = self.correlation_id
    call_entry.stage = stage
    call_entry.assistant_id = assistant_id
    call_entry.success = True
    call_entry.call_duration_ms = call_duration_ms or 0
    
    # Capture input data
    call_entry.input_data = {
        "prompt": self._truncate_text(input_prompt, max_length=10000),
        "prompt_length": len(input_prompt),
        "prompt_hash": hashlib.md5(input_prompt.encode()).hexdigest()
    }
    
    # Capture output data
    response_text = json.dumps(response) if isinstance(response, dict) else str(response)
    call_entry.output_data = {
        "response": self._truncate_text(response_text, max_length=10000),
        "response_length": len(response_text),
        "response_hash": hashlib.md5(response_text.encode()).hexdigest(),
        "token_counts": self._extract_token_counts(response)
    }
    
    # Performance metrics
    call_entry.performance_metrics = {
        "input_tokens": call_entry.output_data["token_counts"].get("input_tokens", 0),
        "output_tokens": call_entry.output_data["token_counts"].get("output_tokens", 0),
        "estimated_cost": self._calculate_estimated_cost(call_entry.output_data["token_counts"])
    }
    
    # Add to session logs
    self.session_logs.append(call_entry)
    self.call_counter += 1
    
    # Update session success count
    if hasattr(self, 'current_session'):
        self.current_session.success_count += 1
        self.current_session.call_logs.append(call_entry.call_id)
    
    # Log to Azure Application Insights
    self._log_to_application_insights(call_entry, "AI_CALL_SUCCESS")
    
    # Log summary to standard logger
    logging.info(
        f"AI call successful - Stage: {stage}, Assistant: {assistant_id[:12]}..., "
        f"Duration: {call_duration_ms}ms, Tokens: {call_entry.performance_metrics.get('input_tokens', 0)}/"
        f"{call_entry.performance_metrics.get('output_tokens', 0)}"
    )
    
    return call_entry.call_id

def log_ai_call_error(self, stage: str, assistant_id: str, error_message: str, 
                     input_prompt: str = None, call_duration_ms: float = None) -> str:
    """
    Log failed AI assistant call with error details
    """
    call_entry = AICallLogEntry()
    call_entry.correlation_id = self.correlation_id
    call_entry.stage = stage
    call_entry.assistant_id = assistant_id
    call_entry.success = False
    call_entry.call_duration_ms = call_duration_ms or 0
    
    # Capture input data if available
    if input_prompt:
        call_entry.input_data = {
            "prompt": self._truncate_text(input_prompt, max_length=10000),
            "prompt_length": len(input_prompt),
            "prompt_hash": hashlib.md5(input_prompt.encode()).hexdigest()
        }
    
    # Capture error details
    call_entry.error_details = {
        "error_message": error_message,
        "error_timestamp": time.time(),
        "error_type": self._classify_error(error_message),
        "recovery_suggestion": self._get_recovery_suggestion(error_message)
    }
    
    # Add to session logs
    self.session_logs.append(call_entry)
    self.call_counter += 1
    
    # Update session error count
    if hasattr(self, 'current_session'):
        self.current_session.error_count += 1
        self.current_session.call_logs.append(call_entry.call_id)
    
    # Log to Azure Application Insights
    self._log_to_application_insights(call_entry, "AI_CALL_ERROR")
    
    # Log error to standard logger
    logging.error(
        f"AI call failed - Stage: {stage}, Assistant: {assistant_id[:12] if assistant_id else 'unknown'}..., "
        f"Error: {error_message}, Duration: {call_duration_ms}ms"
    )
    
    return call_entry.call_id
```

### **3.4 Session Management**
```python
def start_processing_session(self, file_name: str, job_title: str) -> str:
    """
    Initialize new processing session with correlation tracking
    """
    # Create new session
    self.current_session = ProcessingSession(file_name, job_title)
    self.correlation_id = self.current_session.correlation_id
    self.session_start_time = time.time()
    self.session_logs = []
    self.call_counter = 0
    
    # Log session start
    session_start_log = {
        "correlation_id": self.correlation_id,
        "file_name": file_name,
        "job_title": job_title,
        "session_start_time": self.session_start_time,
        "formatted_start_time": datetime.fromtimestamp(self.session_start_time).isoformat()
    }
    
    logging.info(f"Processing session started - CorrelationId: {self.correlation_id}, File: {file_name}")
    
    # Log to Application Insights
    self._log_custom_event("PROCESSING_SESSION_START", session_start_log)
    
    return self.correlation_id

def log_processing_status(self, status: str, details: dict = None):
    """
    Update processing status for current session
    """
    if not self.current_session:
        logging.warning("No active session to update status")
        return
    
    self.current_session.status = status
    
    status_log = {
        "correlation_id": self.correlation_id,
        "status": status,
        "timestamp": time.time(),
        "details": details or {}
    }
    
    # Log status update
    logging.info(f"Processing status updated - CorrelationId: {self.correlation_id}, Status: {status}")
    
    # Log to Application Insights
    self._log_custom_event("PROCESSING_STATUS_UPDATE", status_log)
    
    # If session completed, finalize session
    if status in ["completed", "failed"]:
        self._finalize_session()

def _finalize_session(self):
    """Finalize current processing session"""
    if not self.current_session:
        return
    
    self.current_session.end_time = time.time()
    session_duration = self.current_session.end_time - self.current_session.start_time
    
    # Calculate performance summary
    self.current_session.performance_summary = {
        "total_duration_ms": session_duration * 1000,
        "total_ai_calls": self.call_counter,
        "successful_calls": self.current_session.success_count,
        "failed_calls": self.current_session.error_count,
        "success_rate": (self.current_session.success_count / max(1, self.call_counter)) * 100,
        "total_tokens": sum(entry.performance_metrics.get("input_tokens", 0) + 
                          entry.performance_metrics.get("output_tokens", 0) 
                          for entry in self.session_logs),
        "total_estimated_cost": sum(entry.performance_metrics.get("estimated_cost", 0) 
                                  for entry in self.session_logs)
    }
    
    # Log session completion
    session_summary = {
        "correlation_id": self.correlation_id,
        "file_name": self.current_session.file_name,
        "status": self.current_session.status,
        "duration_ms": session_duration * 1000,
        "performance_summary": self.current_session.performance_summary
    }
    
    logging.info(f"Processing session completed - {session_summary}")
    
    # Log to Application Insights
    self._log_custom_event("PROCESSING_SESSION_COMPLETE", session_summary)
```

## **4. Audit and Compliance Features**

### **4.1 Comprehensive Audit Trail**
```python
def generate_audit_report(self, correlation_id: str) -> dict:
    """
    Generate comprehensive audit report for a processing session
    
    Args:
        correlation_id: Session correlation ID
        
    Returns:
        dict: Complete audit report
    """
    session_logs = [log for log in self.session_logs if log.correlation_id == correlation_id]
    
    if not session_logs:
        return {"error": f"No logs found for correlation ID: {correlation_id}"}
    
    # Organize logs by stage
    logs_by_stage = {}
    for log_entry in session_logs:
        stage = log_entry.stage
        if stage not in logs_by_stage:
            logs_by_stage[stage] = []
        logs_by_stage[stage].append(log_entry.to_dict())
    
    # Calculate aggregated metrics
    total_tokens = sum(log.performance_metrics.get("input_tokens", 0) + 
                      log.performance_metrics.get("output_tokens", 0) 
                      for log in session_logs)
    total_cost = sum(log.performance_metrics.get("estimated_cost", 0) for log in session_logs)
    total_duration = sum(log.call_duration_ms for log in session_logs)
    
    # Generate audit report
    audit_report = {
        "audit_metadata": {
            "correlation_id": correlation_id,
            "report_generated_at": datetime.now().isoformat(),
            "total_ai_calls": len(session_logs),
            "processing_stages": list(logs_by_stage.keys())
        },
        "session_summary": {
            "success_count": sum(1 for log in session_logs if log.success),
            "error_count": sum(1 for log in session_logs if not log.success),
            "total_duration_ms": total_duration,
            "total_tokens_used": total_tokens,
            "total_estimated_cost": round(total_cost, 4)
        },
        "stage_breakdown": logs_by_stage,
        "performance_metrics": {
            "average_call_duration": total_duration / len(session_logs) if session_logs else 0,
            "tokens_per_call": total_tokens / len(session_logs) if session_logs else 0,
            "cost_per_call": total_cost / len(session_logs) if session_logs else 0
        },
        "data_lineage": self._generate_data_lineage(session_logs),
        "compliance_info": {
            "data_retention_period": "90 days",
            "anonymization_applied": True,
            "audit_trail_complete": True
        }
    }
    
    return audit_report

def _generate_data_lineage(self, session_logs: list) -> dict:
    """Generate data lineage information for audit trail"""
    lineage = {
        "input_sources": [],
        "processing_stages": [],
        "output_destinations": [],
        "data_transformations": []
    }
    
    for log_entry in session_logs:
        stage_info = {
            "stage": log_entry.stage,
            "timestamp": log_entry.timestamp,
            "assistant_used": log_entry.assistant_id,
            "input_hash": log_entry.input_data.get("prompt_hash"),
            "output_hash": log_entry.output_data.get("response_hash"),
            "success": log_entry.success
        }
        lineage["processing_stages"].append(stage_info)
    
    return lineage
```

### **4.2 Re-execution Support**
```python
def export_logs_for_replay(self, correlation_id: str) -> dict:
    """
    Export logs in format suitable for replay/re-execution
    
    Args:
        correlation_id: Session correlation ID
        
    Returns:
        dict: Replay-ready log data
    """
    session_logs = [log for log in self.session_logs if log.correlation_id == correlation_id]
    
    replay_data = {
        "replay_metadata": {
            "original_correlation_id": correlation_id,
            "export_timestamp": time.time(),
            "total_calls": len(session_logs)
        },
        "replay_calls": []
    }
    
    for log_entry in session_logs:
        if log_entry.success:  # Only export successful calls for replay
            replay_call = {
                "stage": log_entry.stage,
                "assistant_id": log_entry.assistant_id,
                "input_prompt": log_entry.input_data.get("prompt"),
                "expected_response_hash": log_entry.output_data.get("response_hash"),
                "original_timestamp": log_entry.timestamp,
                "original_duration_ms": log_entry.call_duration_ms
            }
            replay_data["replay_calls"].append(replay_call)
    
    return replay_data

def replay_ai_call(self, replay_call_data: dict, openai_service) -> dict:
    """
    Replay a specific AI call using saved data
    
    Args:
        replay_call_data: Replay call data from export
        openai_service: OpenAI service instance
        
    Returns:
        dict: Replay results with comparison to original
    """
    try:
        # Execute replay call
        start_time = time.time()
        response = openai_service.call_assistant(
            assistant_id=replay_call_data["assistant_id"],
            prompt=replay_call_data["input_prompt"]
        )
        call_duration = (time.time() - start_time) * 1000
        
        # Compare with original
        response_text = json.dumps(response)
        new_response_hash = hashlib.md5(response_text.encode()).hexdigest()
        
        replay_result = {
            "replay_successful": True,
            "original_response_hash": replay_call_data["expected_response_hash"],
            "new_response_hash": new_response_hash,
            "responses_match": new_response_hash == replay_call_data["expected_response_hash"],
            "original_duration_ms": replay_call_data["original_duration_ms"],
            "new_duration_ms": call_duration,
            "performance_delta": call_duration - replay_call_data["original_duration_ms"]
        }
        
        return replay_result
        
    except Exception as e:
        return {
            "replay_successful": False,
            "error_message": str(e)
        }
```

## **5. Performance Analytics and Reporting**

### **5.1 Performance Metrics Collection**
```python
def log_performance_metrics(self, metrics: dict):
    """
    Log performance metrics for analysis
    
    Args:
        metrics: Performance metrics dictionary
    """
    performance_log = {
        "correlation_id": self.correlation_id,
        "timestamp": time.time(),
        "metrics": metrics
    }
    
    # Add to performance analytics
    self._track_performance_trends(metrics)
    
    # Log to Application Insights
    self._log_custom_event("PERFORMANCE_METRICS", performance_log)

def _track_performance_trends(self, metrics: dict):
    """Track performance trends over time"""
    # This could be enhanced to use a time-series database
    # For now, we'll use in-memory tracking
    if not hasattr(self, 'performance_history'):
        self.performance_history = []
    
    self.performance_history.append({
        "timestamp": time.time(),
        "metrics": metrics
    })
    
    # Keep only last 100 entries to prevent memory issues
    if len(self.performance_history) > 100:
        self.performance_history = self.performance_history[-100:]

def get_performance_analytics(self, time_range_hours: int = 24) -> dict:
    """
    Get performance analytics for specified time range
    
    Args:
        time_range_hours: Time range for analysis
        
    Returns:
        dict: Performance analytics report
    """
    cutoff_time = time.time() - (time_range_hours * 3600)
    recent_logs = [log for log in self.session_logs if log.timestamp > cutoff_time]
    
    if not recent_logs:
        return {"message": "No data available for specified time range"}
    
    # Calculate analytics
    successful_calls = [log for log in recent_logs if log.success]
    failed_calls = [log for log in recent_logs if not log.success]
    
    analytics = {
        "time_range_hours": time_range_hours,
        "total_calls": len(recent_logs),
        "success_rate": (len(successful_calls) / len(recent_logs)) * 100,
        "average_duration_ms": sum(log.call_duration_ms for log in recent_logs) / len(recent_logs),
        "total_tokens": sum(log.performance_metrics.get("input_tokens", 0) + 
                          log.performance_metrics.get("output_tokens", 0) 
                          for log in recent_logs),
        "total_cost": sum(log.performance_metrics.get("estimated_cost", 0) for log in recent_logs),
        "stage_performance": self._analyze_stage_performance(recent_logs),
        "error_analysis": self._analyze_errors(failed_calls)
    }
    
    return analytics

def _analyze_stage_performance(self, logs: list) -> dict:
    """Analyze performance by processing stage"""
    stage_stats = {}
    
    for log in logs:
        stage = log.stage
        if stage not in stage_stats:
            stage_stats[stage] = {
                "call_count": 0,
                "success_count": 0,
                "total_duration": 0,
                "total_tokens": 0,
                "total_cost": 0
            }
        
        stats = stage_stats[stage]
        stats["call_count"] += 1
        if log.success:
            stats["success_count"] += 1
        stats["total_duration"] += log.call_duration_ms
        stats["total_tokens"] += (log.performance_metrics.get("input_tokens", 0) + 
                                log.performance_metrics.get("output_tokens", 0))
        stats["total_cost"] += log.performance_metrics.get("estimated_cost", 0)
    
    # Calculate averages
    for stage, stats in stage_stats.items():
        stats["success_rate"] = (stats["success_count"] / stats["call_count"]) * 100
        stats["average_duration"] = stats["total_duration"] / stats["call_count"]
        stats["average_tokens"] = stats["total_tokens"] / stats["call_count"]
        stats["average_cost"] = stats["total_cost"] / stats["call_count"]
    
    return stage_stats
```

## **6. Integration with Azure Application Insights**

### **6.1 Application Insights Integration**
```python
def _initialize_logger(self):
    """Initialize logging with Azure Application Insights integration"""
    # Configure standard Python logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Application Insights integration (if available)
    self.app_insights_enabled = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING") is not None
    
    if self.app_insights_enabled:
        try:
            from opencensus.ext.azure.log_exporter import AzureLogHandler
            self.azure_logger = logging.getLogger(__name__)
            self.azure_logger.addHandler(AzureLogHandler())
        except ImportError:
            logging.warning("Azure Application Insights not available - continuing with standard logging")
            self.app_insights_enabled = False

def _log_to_application_insights(self, log_entry: AICallLogEntry, event_type: str):
    """Log entry to Azure Application Insights"""
    if not self.app_insights_enabled:
        return
    
    try:
        # Create custom event for Application Insights
        custom_event = {
            "name": event_type,
            "properties": {
                "correlation_id": log_entry.correlation_id,
                "stage": log_entry.stage,
                "assistant_id": log_entry.assistant_id,
                "success": log_entry.success,
                "duration_ms": log_entry.call_duration_ms,
                "input_tokens": log_entry.performance_metrics.get("input_tokens", 0),
                "output_tokens": log_entry.performance_metrics.get("output_tokens", 0),
                "estimated_cost": log_entry.performance_metrics.get("estimated_cost", 0)
            }
        }
        
        if not log_entry.success and log_entry.error_details:
            custom_event["properties"]["error_message"] = log_entry.error_details.get("error_message")
            custom_event["properties"]["error_type"] = log_entry.error_details.get("error_type")
        
        # Send to Application Insights
        self.azure_logger.info("AI Call Event", extra={"custom_dimensions": custom_event})
        
    except Exception as e:
        logging.warning(f"Failed to log to Application Insights: {str(e)}")

def _log_custom_event(self, event_name: str, properties: dict):
    """Log custom event to Application Insights"""
    if not self.app_insights_enabled:
        return
    
    try:
        self.azure_logger.info(event_name, extra={"custom_dimensions": properties})
    except Exception as e:
        logging.warning(f"Failed to log custom event to Application Insights: {str(e)}")
```

## **7. Utility Functions**

### **7.1 Helper Functions**
```python
def _truncate_text(self, text: str, max_length: int = 10000) -> str:
    """Truncate text to specified length for logging"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + f"... [TRUNCATED - Original length: {len(text)}]"

def _extract_token_counts(self, response: dict) -> dict:
    """Extract token counts from AI response"""
    token_counts = {
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0
    }
    
    # Try to extract from response if available
    if isinstance(response, dict):
        usage = response.get("usage", {})
        token_counts["input_tokens"] = usage.get("prompt_tokens", 0)
        token_counts["output_tokens"] = usage.get("completion_tokens", 0)
        token_counts["total_tokens"] = usage.get("total_tokens", 0)
    
    return token_counts

def _calculate_estimated_cost(self, token_counts: dict) -> float:
    """Calculate estimated cost based on token usage"""
    input_tokens = token_counts.get("input_tokens", 0)
    output_tokens = token_counts.get("output_tokens", 0)
    
    # GPT-4o-mini pricing
    input_cost = (input_tokens / 1000) * 0.00015
    output_cost = (output_tokens / 1000) * 0.0006
    
    return round(input_cost + output_cost, 6)

def _classify_error(self, error_message: str) -> str:
    """Classify error type based on error message"""
    error_message_lower = error_message.lower()
    
    if "timeout" in error_message_lower:
        return "timeout_error"
    elif "rate limit" in error_message_lower:
        return "rate_limit_error"
    elif "authentication" in error_message_lower:
        return "authentication_error"
    elif "connection" in error_message_lower:
        return "connection_error"
    elif "validation" in error_message_lower:
        return "validation_error"
    else:
        return "unknown_error"

def _get_recovery_suggestion(self, error_message: str) -> str:
    """Get recovery suggestion based on error type"""
    error_type = self._classify_error(error_message)
    
    suggestions = {
        "timeout_error": "Retry with exponential backoff",
        "rate_limit_error": "Wait and retry after rate limit reset",
        "authentication_error": "Check API credentials and permissions",
        "connection_error": "Check network connectivity and retry",
        "validation_error": "Validate input data and retry",
        "unknown_error": "Manual investigation required"
    }
    
    return suggestions.get(error_type, "Contact support for assistance")
```

## **8. Configuration and Dependencies**

### **8.1 Configuration Constants**
```python
# Logging configuration
LOGGING_CONFIG = {
    "max_log_retention_days": 90,
    "max_prompt_log_length": 10000,
    "max_response_log_length": 10000,
    "enable_detailed_logging": True,
    "enable_performance_tracking": True
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "slow_call_threshold_ms": 10000,
    "high_token_usage_threshold": 5000,
    "high_cost_threshold": 0.50
}
```

### **8.2 Dependencies**
```txt
opencensus-ext-azure>=1.1.0    # Azure Application Insights integration
hashlib                        # Built-in Python module
uuid                          # Built-in Python module
datetime                      # Built-in Python module
json                          # Built-in Python module
```

## **9. Integration Requirements**

### **9.1 Integration Points**
- **Used by:** `OpenAIService` for all AI call logging
- **Used by:** `CandidateDataService` for processing status updates
- **Used by:** `function_app.py` for session management
- **Outputs to:** Azure Application Insights, standard Python logging

### **9.2 Environment Variables**
```python
OPTIONAL_ENV_VARS = {
    "APPLICATIONINSIGHTS_CONNECTION_STRING": "Azure Application Insights connection string",
    "LOG_LEVEL": "Logging level (DEBUG, INFO, WARNING, ERROR)",
    "ENABLE_DETAILED_LOGGING": "Enable detailed AI call logging (true/false)"
}
```

---

**Next Steps:**
- Implement AICallLogger class with comprehensive logging capabilities
- Add Azure Application Insights integration
- Create audit and compliance reporting features
- Implement performance analytics and trending
- Add re-execution and replay capabilities
- Create comprehensive unit tests for all logging scenarios

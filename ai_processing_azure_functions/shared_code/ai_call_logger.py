"""
AI Call Logger Module
AI-Powered CV Processing Engine for TTE Recruitment Suite

This module provides comprehensive logging for all AI assistant calls,
enabling debugging, auditing, and re-execution capabilities.

Version: 1.0
Date: September 23, 2025
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class AICallLogger:
    """
    Service class for logging AI assistant calls with comprehensive details
    """
    
    def __init__(self):
        """Initialize the AI call logger"""
        self.max_prompt_length = 10000  # Truncate prompts longer than this
        logger.info("AI call logger initialized")
    
    def create_call_log(
        self,
        stage: str,
        assistant_id: str,
        model_used: str,
        input_prompt: str,
        input_tokens: int,
        response_text: str,
        output_tokens: int,
        call_duration_ms: float,
        call_timestamp: str,
        success: bool,
        error_details: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive log entry for an AI assistant call
        
        Args:
            stage: Processing stage (candidate_data_extraction, pii_identification, skills_analysis)
            assistant_id: Azure OpenAI Assistant ID
            model_used: Model name used for the call
            input_prompt: Input prompt sent to the assistant
            input_tokens: Number of input tokens used
            response_text: Response text received from the assistant
            output_tokens: Number of output tokens used
            call_duration_ms: Duration of the call in milliseconds
            call_timestamp: ISO timestamp of when the call was made
            success: Whether the call was successful
            error_details: Error details if the call failed
            
        Returns:
            Dict containing the structured log entry
        """
        
        # Truncate prompt if too long
        truncated_prompt = input_prompt
        if len(input_prompt) > self.max_prompt_length:
            truncated_prompt = input_prompt[:self.max_prompt_length] + "... [TRUNCATED]"
            logger.warning(f"Input prompt truncated for logging. Original length: {len(input_prompt)}")
        
        # Create log entry
        log_entry = {
            "stage": stage,
            "assistantId": assistant_id,
            "modelUsed": model_used,
            "inputPrompt": truncated_prompt,
            "inputTokens": input_tokens,
            "responseText": response_text,
            "outputTokens": output_tokens,
            "callDurationMs": round(call_duration_ms, 2),
            "callTimestamp": call_timestamp,
            "success": success,
            "errorDetails": error_details
        }
        
        # Log the call details
        if success:
            logger.info(f"AI call logged - Stage: {stage}, Duration: {call_duration_ms:.2f}ms, Tokens: {input_tokens + output_tokens}")
        else:
            logger.error(f"Failed AI call logged - Stage: {stage}, Error: {error_details}")
        
        return log_entry
    
    def log_processing_session(
        self,
        correlation_id: str,
        session_start: datetime,
        session_end: datetime,
        all_call_logs: list,
        total_tokens: int,
        estimated_cost: str,
        session_success: bool
    ) -> Dict[str, Any]:
        """
        Create a comprehensive log for an entire processing session
        
        Args:
            correlation_id: Unique session identifier
            session_start: Session start timestamp
            session_end: Session end timestamp
            all_call_logs: List of all AI call logs in the session
            total_tokens: Total tokens used across all calls
            estimated_cost: Estimated cost for the session
            session_success: Whether the overall session was successful
            
        Returns:
            Dict containing the session log
        """
        
        session_duration_ms = (session_end - session_start).total_seconds() * 1000
        
        session_log = {
            "correlationId": correlation_id,
            "sessionStartTimestamp": session_start.isoformat() + 'Z',
            "sessionEndTimestamp": session_end.isoformat() + 'Z',
            "sessionDurationMs": round(session_duration_ms, 2),
            "totalAiCalls": len(all_call_logs),
            "successfulCalls": len([log for log in all_call_logs if log.get('success', False)]),
            "failedCalls": len([log for log in all_call_logs if not log.get('success', True)]),
            "totalTokensUsed": total_tokens,
            "estimatedCost": estimated_cost,
            "sessionSuccess": session_success,
            "stageBreakdown": self._create_stage_breakdown(all_call_logs),
            "allCallLogs": all_call_logs
        }
        
        logger.info(f"Processing session logged - CorrelationId: {correlation_id}, Duration: {session_duration_ms:.2f}ms, Success: {session_success}")
        
        return session_log
    
    def _create_stage_breakdown(self, all_call_logs: list) -> Dict[str, Any]:
        """
        Create a breakdown of processing by stage
        
        Args:
            all_call_logs: List of all AI call logs
            
        Returns:
            Dict with stage-wise breakdown
        """
        stage_breakdown = {}
        
        for log in all_call_logs:
            stage = log.get('stage', 'unknown')
            
            if stage not in stage_breakdown:
                stage_breakdown[stage] = {
                    "callCount": 0,
                    "successfulCalls": 0,
                    "totalDurationMs": 0,
                    "totalInputTokens": 0,
                    "totalOutputTokens": 0,
                    "avgDurationMs": 0
                }
            
            stage_data = stage_breakdown[stage]
            stage_data["callCount"] += 1
            
            if log.get('success', False):
                stage_data["successfulCalls"] += 1
            
            stage_data["totalDurationMs"] += log.get('callDurationMs', 0)
            stage_data["totalInputTokens"] += log.get('inputTokens', 0)
            stage_data["totalOutputTokens"] += log.get('outputTokens', 0)
            
            # Calculate average duration
            stage_data["avgDurationMs"] = stage_data["totalDurationMs"] / stage_data["callCount"]
        
        return stage_breakdown
    
    def create_error_log(
        self,
        stage: str,
        error_type: str,
        error_message: str,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a structured error log entry
        
        Args:
            stage: Processing stage where error occurred
            error_type: Type of error (VALIDATION_ERROR, PROCESSING_ERROR, etc.)
            error_message: Detailed error message
            context: Additional context information
            correlation_id: Session correlation ID
            
        Returns:
            Dict containing the error log entry
        """
        
        error_log = {
            "logType": "error",
            "errorId": str(uuid.uuid4()),
            "correlationId": correlation_id,
            "timestamp": datetime.utcnow().isoformat() + 'Z',
            "stage": stage,
            "errorType": error_type,
            "errorMessage": error_message,
            "context": context,
            "severity": self._determine_error_severity(error_type)
        }
        
        logger.error(f"Error logged - Stage: {stage}, Type: {error_type}, Message: {error_message}")
        
        return error_log
    
    def _determine_error_severity(self, error_type: str) -> str:
        """
        Determine error severity based on error type
        
        Args:
            error_type: Type of error
            
        Returns:
            Severity level string
        """
        high_severity_errors = [
            "CONFIGURATION_ERROR",
            "AUTHENTICATION_ERROR",
            "UNEXPECTED_ERROR"
        ]
        
        medium_severity_errors = [
            "PROCESSING_ERROR",
            "AI_SERVICE_ERROR",
            "TIMEOUT_ERROR"
        ]
        
        if error_type in high_severity_errors:
            return "HIGH"
        elif error_type in medium_severity_errors:
            return "MEDIUM"
        else:
            return "LOW"
    
    def export_logs_for_debugging(
        self,
        correlation_id: str,
        logs: list,
        include_prompts: bool = True,
        include_responses: bool = True
    ) -> str:
        """
        Export logs in a format suitable for debugging
        
        Args:
            correlation_id: Session correlation ID
            logs: List of log entries
            include_prompts: Whether to include full prompts
            include_responses: Whether to include full responses
            
        Returns:
            JSON string with formatted logs
        """
        
        debug_logs = {
            "correlationId": correlation_id,
            "exportTimestamp": datetime.utcnow().isoformat() + 'Z',
            "totalLogs": len(logs),
            "logs": []
        }
        
        for log in logs:
            debug_log = log.copy()
            
            # Optionally exclude prompts and responses to reduce size
            if not include_prompts and "inputPrompt" in debug_log:
                debug_log["inputPrompt"] = "[EXCLUDED_FOR_BREVITY]"
            
            if not include_responses and "responseText" in debug_log:
                debug_log["responseText"] = "[EXCLUDED_FOR_BREVITY]"
            
            debug_logs["logs"].append(debug_log)
        
        return json.dumps(debug_logs, indent=2)
    
    def create_performance_metrics(self, all_call_logs: list) -> Dict[str, Any]:
        """
        Create performance metrics from call logs
        
        Args:
            all_call_logs: List of all AI call logs
            
        Returns:
            Dict with performance metrics
        """
        
        if not all_call_logs:
            return {"error": "No call logs provided"}
        
        total_calls = len(all_call_logs)
        successful_calls = len([log for log in all_call_logs if log.get('success', False)])
        failed_calls = total_calls - successful_calls
        
        durations = [log.get('callDurationMs', 0) for log in all_call_logs if log.get('success', False)]
        input_tokens = [log.get('inputTokens', 0) for log in all_call_logs]
        output_tokens = [log.get('outputTokens', 0) for log in all_call_logs]
        
        metrics = {
            "totalCalls": total_calls,
            "successfulCalls": successful_calls,
            "failedCalls": failed_calls,
            "successRate": round((successful_calls / total_calls) * 100, 2) if total_calls > 0 else 0,
            "averageDurationMs": round(sum(durations) / len(durations), 2) if durations else 0,
            "minDurationMs": min(durations) if durations else 0,
            "maxDurationMs": max(durations) if durations else 0,
            "totalInputTokens": sum(input_tokens),
            "totalOutputTokens": sum(output_tokens),
            "averageInputTokens": round(sum(input_tokens) / len(input_tokens), 2) if input_tokens else 0,
            "averageOutputTokens": round(sum(output_tokens) / len(output_tokens), 2) if output_tokens else 0
        }
        
        return metrics

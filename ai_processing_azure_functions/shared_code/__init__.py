"""
Shared Code Package for AI-Powered CV Processing Engine

This package contains shared modules for document processing, AI service interactions,
candidate data extraction, and logging functionality.

Version: 1.0
Date: September 23, 2025
"""

# Make modules available at package level
from .document_processor import extract_markdown_from_file, UnsupportedFileType, DocumentProcessingError
from .candidate_data_service import CandidateDataService
from .openai_service import OpenAIService, OpenAIResponse
from .ai_call_logger import AICallLogger

__all__ = [
    'extract_markdown_from_file',
    'UnsupportedFileType', 
    'DocumentProcessingError',
    'CandidateDataService',
    'OpenAIService',
    'OpenAIResponse',
    'AICallLogger'
]

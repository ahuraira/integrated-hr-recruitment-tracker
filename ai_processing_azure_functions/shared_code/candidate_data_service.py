"""
Candidate Data Service Module
AI-Powered CV Processing Engine for TTE Recruitment Suite

This module handles candidate data extraction, PII identification and anonymization,
and skills analysis using Azure OpenAI assistants.

Version: 1.0
Date: September 23, 2025
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import AI service modules (to be implemented)
from .openai_service import OpenAIService
from .ai_call_logger import AICallLogger

logger = logging.getLogger(__name__)

class CandidateDataService:
    """
    Service class for extracting candidate data and performing PII anonymization
    """
    
    def __init__(self):
        """Initialize the candidate data service"""
        self.openai_service = OpenAIService()
        self.ai_logger = AICallLogger()
    
    def extract_candidate_data(self, markdown_content: str, job_title: str) -> Dict[str, Any]:
        """
        Main orchestration method for the three-stage AI pipeline
        
        Args:
            markdown_content: CV text in markdown format
            job_title: Target job title from MPR
            
        Returns:
            Dict containing all processing results
        """
        logger.info("Starting three-stage AI pipeline for candidate data extraction")
        
        all_logs = []
        candidate_data = {}
        pii_data = {}
        anonymized_content = ""
        analysis_data = {}
        
        # Stage 1: Candidate Data Extraction
        try:
            logger.info("Stage 1: Extracting candidate data")
            candidate_data, candidate_log = self._extract_candidate_profile(markdown_content, job_title)
            all_logs.append(candidate_log)
        except Exception as e:
            logger.error(f"Stage 1 failed: {str(e)}")
            # Log the failure but continue if possible (though Stage 1 is usually critical)
            # In this design, we'll try to proceed or return what we have
            # For now, let's assume we can't really proceed without candidate data, but we want to return the log
            pass # The error is already logged inside _extract_candidate_profile if it uses the logger correctly, 
                 # BUT _extract_candidate_profile raises exception. We need to catch it here to preserve the log?
                 # Actually _extract_candidate_profile raises exception AFTER logging. 
                 # We need to make sure we capture that log.
                 # Let's look at _extract_candidate_profile: it raises Exception.
                 # So we need to catch it here.
            
            # Wait, _extract_candidate_profile creates an error log but doesn't return it if it raises.
            # We need to modify _extract_candidate_profile to return the log even on failure OR handle it here.
            # Better approach: The helper methods raise exception. We should catch it, 
            # but we can't get the log from the helper if it raises.
            # So we should probably rely on the helper to log to the DB? No, the logger just returns a dict.
            # We need to construct the error log here if the helper fails, OR modify helpers.
            
            # Actually, looking at the existing code, helpers create an error log and THEN raise.
            # But they don't return the log.
            # So we lose that log object.
            # I will modify this method to construct the error log here if needed, 
            # OR better: catch the exception which hopefully contains details, and create a log entry here.
            
            # Let's stick to the plan: wrap each stage.
            # Since helpers raise, we need to create the error log here to append to all_logs.
            
            error_log = self.ai_logger.create_call_log(
                stage="candidate_data_extraction",
                assistant_id=self.openai_service.get_assistant_id("CV_DATA_EXTRACTOR"),
                model_used="gpt-4o-mini",
                input_prompt="[FAILED_BEFORE_COMPLETION]", 
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=0,
                call_timestamp=datetime.utcnow().isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            all_logs.append(error_log)
            # If Stage 1 fails, we probably can't do much else useful, but we return what we have.
            return self._build_final_result(candidate_data, analysis_data, all_logs, pii_data, anonymized_content)

        # Stage 2: PII Identification and Anonymization
        try:
            logger.info("Stage 2: Identifying PII and creating anonymized content")
            pii_data, anonymized_content, pii_log = self._identify_and_anonymize_pii(markdown_content)
            all_logs.append(pii_log)
        except Exception as e:
            logger.error(f"Stage 2 failed: {str(e)}")
            error_log = self.ai_logger.create_call_log(
                stage="pii_identification",
                assistant_id=self.openai_service.get_assistant_id("CV_PII_IDENTIFIER"),
                model_used="gpt-4o-mini",
                input_prompt="[FAILED_BEFORE_COMPLETION]",
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=0,
                call_timestamp=datetime.utcnow().isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            all_logs.append(error_log)
            # If Stage 2 fails, we cannot do Stage 3 (needs anonymized content)
            return self._build_final_result(candidate_data, analysis_data, all_logs, pii_data, anonymized_content)

        # Stage 3: Skills and Experience Analysis
        try:
            logger.info("Stage 3: Analyzing skills and experience")
            analysis_data, analysis_log = self._analyze_skills_and_experience(anonymized_content, job_title)
            all_logs.append(analysis_log)
        except Exception as e:
            logger.error(f"Stage 3 failed: {str(e)}")
            error_log = self.ai_logger.create_call_log(
                stage="skills_analysis",
                assistant_id=self.openai_service.get_assistant_id("CV_SKILLS_ANALYST"),
                model_used="gpt-4o-mini",
                input_prompt="[FAILED_BEFORE_COMPLETION]",
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=0,
                call_timestamp=datetime.utcnow().isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            all_logs.append(error_log)
            # Return what we have (Stage 1 & 2 successful, Stage 3 failed)
            return self._build_final_result(candidate_data, analysis_data, all_logs, pii_data, anonymized_content)
        
        # All stages successful
        logger.info("Three-stage AI pipeline completed successfully")
        return self._build_final_result(candidate_data, analysis_data, all_logs, pii_data, anonymized_content)

    def _build_final_result(self, candidate_data, analysis_data, all_logs, pii_data, anonymized_content):
        """Helper to build the final result dictionary"""
        token_summary = self._calculate_token_summary(all_logs)
        return {
            'candidateProfile': candidate_data,
            'professionalAnalysis': analysis_data,
            'aiCallLogs': all_logs,
            'tokenUsageSummary': token_summary,
            'piiData': pii_data,
            'anonymizedContent': anonymized_content
        }
    
    def _extract_candidate_profile(self, markdown_content: str, job_title: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Stage 1: Extract structured candidate information using CV-Data-Extractor assistant
        
        Args:
            markdown_content: CV text in markdown format
            job_title: Target job title
            
        Returns:
            Tuple of (candidate_data, ai_call_log)
        """
        logger.info("Extracting candidate profile data")
        
        # First try regex extraction for highly structured data
        regex_data = self._extract_with_regex(markdown_content)
        
        # Prepare prompt for AI assistant
        prompt = f"""
        Extract structured candidate information from the following CV text.
        Target job title: {job_title}
        
        CV Content:
        {markdown_content}
        
        Extract all available information according to the required JSON schema.
        Use the target job title for the jobTitle field.
        If any information is not available, return null for that field.
        Ensure numeric fields (experience years, salary) are extracted as numbers when possible.
        Include currency information for salary fields if mentioned.
        """
        
        # Call Azure OpenAI Assistant
        start_time = datetime.utcnow()
        try:
            response = self.openai_service.call_assistant(
                assistant_type="CV_DATA_EXTRACTOR",
                prompt=prompt
            )
            
            # Parse the JSON response
            candidate_data = json.loads(response.content)['candidateProfile']
            
            # Merge with regex data - AI takes precedence, regex only fills missing fields
            for key, value in regex_data.items():
                if key not in candidate_data or not candidate_data.get(key):
                    candidate_data[key] = value
                    logger.debug(f"Using regex fallback for {key}")
                else:
                    logger.debug(f"Preserving AI-extracted value for {key}, ignoring regex")
            
            # Create AI call log
            call_log = self.ai_logger.create_call_log(
                stage="candidate_data_extraction",
                assistant_id=self.openai_service.get_assistant_id("CV_DATA_EXTRACTOR"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=response.usage.prompt_tokens,
                response_text=response.content,
                output_tokens=response.usage.completion_tokens,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=True
            )
            
            logger.info("Candidate profile extraction completed successfully")
            return candidate_data, call_log
            
        except Exception as e:
            logger.error(f"Error in candidate profile extraction: {str(e)}")
            
            # Create error log
            call_log = self.ai_logger.create_call_log(
                stage="candidate_data_extraction",
                assistant_id=self.openai_service.get_assistant_id("CV_DATA_EXTRACTOR"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            
            raise Exception(f"Candidate profile extraction failed: {str(e)}")
    
    def _extract_with_regex(self, text: str) -> Dict[str, Any]:
        """
        Extract highly structured data using regular expressions
        
        Args:
            text: CV text content
            
        Returns:
            Dict with extracted structured data
        """
        regex_data = {}
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            regex_data['candidateEmail'] = emails[0]
        
        # Phone number extraction (various formats)
        phone_patterns = [
            r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
            r'\(\d{3}\)\s*\d{3}-\d{4}',
            r'\d{3}-\d{3}-\d{4}'
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                regex_data['candidatePhone'] = phones[0]
                break
        
        # LinkedIn URL extraction
        linkedin_pattern = r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+'
        linkedin_urls = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_urls:
            regex_data['linkedInUrl'] = linkedin_urls[0]
        
        # Portfolio/GitHub URLs
        url_patterns = [
            r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+',
            r'(?:https?://)?[a-zA-Z0-9_-]+\.(?:dev|com|io|org)/?\w*'
        ]
        
        other_urls = []
        for pattern in url_patterns:
            urls = re.findall(pattern, text, re.IGNORECASE)
            other_urls.extend([url for url in urls if 'linkedin' not in url.lower()])
        
        if other_urls:
            regex_data['otherProfileUrls'] = list(set(other_urls))
        
        return regex_data
    
    def _identify_and_anonymize_pii(self, markdown_content: str) -> tuple[Dict[str, Any], str, Dict[str, Any]]:
        """
        Stage 2: Identify PII entities and create anonymized content
        
        Args:
            markdown_content: CV text in markdown format
            
        Returns:
            Tuple of (pii_data, anonymized_content, ai_call_log)
        """
        logger.info("Identifying PII entities")
        
        prompt = f"""
        Identify all Personally Identifiable Information (PII) entities in the following CV text.
        Focus on names, organizations, schools, addresses, certification numbers, and other identifying information.
        
        CV Content:
        {markdown_content}
        
        Return a structured list of PII entities with their types, sensitivity levels, and context.
        """
        
        start_time = datetime.utcnow()
        try:
            response = self.openai_service.call_assistant(
                assistant_type="CV_PII_IDENTIFIER",
                prompt=prompt
            )
            
            # Parse PII entities
            pii_response = json.loads(response.content)
            pii_entities = pii_response['pii_entities']
            
            # Create anonymized content programmatically
            anonymized_content = self._create_anonymized_content(markdown_content, pii_entities)
            
            # Create AI call log
            call_log = self.ai_logger.create_call_log(
                stage="pii_identification",
                assistant_id=self.openai_service.get_assistant_id("CV_PII_IDENTIFIER"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=response.usage.prompt_tokens,
                response_text=response.content,
                output_tokens=response.usage.completion_tokens,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=True
            )
            
            logger.info(f"PII identification completed. Found {len(pii_entities)} PII entities")
            return pii_response, anonymized_content, call_log
            
        except Exception as e:
            logger.error(f"Error in PII identification: {str(e)}")
            
            # Create error log
            call_log = self.ai_logger.create_call_log(
                stage="pii_identification",
                assistant_id=self.openai_service.get_assistant_id("CV_PII_IDENTIFIER"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            
            raise Exception(f"PII identification failed: {str(e)}")
    
    def _create_anonymized_content(self, original_content: str, pii_entities: List[Dict[str, Any]]) -> str:
        """
        Create anonymized content by replacing PII with deterministic placeholders
        
        Args:
            original_content: Original CV text
            pii_entities: List of identified PII entities
            
        Returns:
            Anonymized content with placeholders
        """
        anonymized_content = original_content
        replacement_map = {}
        entity_counters = {}
        
        # Sort entities by length (longest first) to avoid partial replacements
        sorted_entities = sorted(pii_entities, key=lambda x: len(x['original_value']), reverse=True)
        
        for entity in sorted_entities:
            pii_type = entity['pii_type']
            original_value = entity['original_value']
            
            # Generate deterministic placeholder
            if pii_type not in entity_counters:
                entity_counters[pii_type] = 0
            
            entity_counters[pii_type] += 1
            
            # Create placeholder based on type
            if pii_type == 'name':
                placeholder = '[CANDIDATE_NAME]'
            elif pii_type == 'organization':
                placeholder = f'[COMPANY_{entity_counters[pii_type]}]'
            elif pii_type == 'school':
                placeholder = f'[UNIVERSITY_{entity_counters[pii_type]}]'
            elif pii_type == 'address':
                placeholder = f'[ADDRESS_{entity_counters[pii_type]}]'
            elif pii_type == 'job_title':
                placeholder = f'[JOB_TITLE_{entity_counters[pii_type]}]'
            elif pii_type == 'certification_number':
                placeholder = f'[CERT_NUMBER_{entity_counters[pii_type]}]'
            elif pii_type == 'license_number':
                placeholder = f'[LICENSE_NUMBER_{entity_counters[pii_type]}]'
            elif pii_type == 'national_id':
                placeholder = f'[NATIONAL_ID_{entity_counters[pii_type]}]'
            else:
                placeholder = f'[{pii_type.upper()}_{entity_counters[pii_type]}]'
            
            # Replace all variations of the entity
            for variation in entity['all_variations']:
                if variation in anonymized_content:
                    anonymized_content = anonymized_content.replace(variation, placeholder)
                    replacement_map[variation] = placeholder
        
        logger.info(f"Created anonymized content with {len(replacement_map)} replacements")
        return anonymized_content
    
    def _analyze_skills_and_experience(self, anonymized_content: str, job_title: str) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Stage 3: Analyze skills and experience using anonymized content
        
        Args:
            anonymized_content: PII-anonymized CV text
            job_title: Target job title
            
        Returns:
            Tuple of (analysis_data, ai_call_log)
        """
        logger.info("Analyzing skills and experience")
        
        prompt = f"""
        Analyze the professional skills and experience from the following anonymized CV text.
        Target job title: {job_title}
        
        Anonymized CV Content:
        {anonymized_content}
        
        Provide a comprehensive analysis including:
        - AI confidence score for the extraction quality
        - Overall fit score for the target role
        - Core skills with proficiency levels
        - Work experience summary
        - Education profile
        - Detailed AI remarks about the candidate's suitability
        """
        
        start_time = datetime.utcnow()
        try:
            response = self.openai_service.call_assistant(
                assistant_type="CV_SKILLS_ANALYST",
                prompt=prompt
            )
            
            # Parse analysis response
            analysis_response = json.loads(response.content)
            
            # Extract analysis metrics and professional profile
            analysis_data = {
                'aiConfidenceScore': analysis_response['analysisMetrics']['aiConfidenceScore'],
                'aiRemarks': analysis_response['analysisMetrics']['aiRemarks'],
                'overallFitScore': analysis_response['analysisMetrics']['overallFitScore'],
                'coreSkills': analysis_response['professionalProfile']['coreSkills'],
                'workExperience': analysis_response['professionalProfile']['workExperience'],
                'educationProfile': analysis_response['professionalProfile']['educationProfile']
            }
            
            # Create AI call log
            call_log = self.ai_logger.create_call_log(
                stage="skills_analysis",
                assistant_id=self.openai_service.get_assistant_id("CV_SKILLS_ANALYST"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=response.usage.prompt_tokens,
                response_text=response.content,
                output_tokens=response.usage.completion_tokens,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=True
            )
            
            logger.info("Skills and experience analysis completed successfully")
            return analysis_data, call_log
            
        except Exception as e:
            logger.error(f"Error in skills analysis: {str(e)}")
            
            # Create error log
            call_log = self.ai_logger.create_call_log(
                stage="skills_analysis",
                assistant_id=self.openai_service.get_assistant_id("CV_SKILLS_ANALYST"),
                model_used="gpt-4o-mini",
                input_prompt=prompt,
                input_tokens=0,
                response_text="",
                output_tokens=0,
                call_duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                call_timestamp=start_time.isoformat() + 'Z',
                success=False,
                error_details=str(e)
            )
            
            raise Exception(f"Skills analysis failed: {str(e)}")
    
    def _calculate_token_summary(self, ai_call_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate token usage summary from all AI calls
        
        Args:
            ai_call_logs: List of AI call logs
            
        Returns:
            Token usage summary
        """
        total_input_tokens = sum(log.get('inputTokens', 0) for log in ai_call_logs)
        total_output_tokens = sum(log.get('outputTokens', 0) for log in ai_call_logs)
        total_tokens = total_input_tokens + total_output_tokens
        
        # Estimate cost (rough estimate for gpt-4o-mini)
        # Input: $0.00015 per 1K tokens, Output: $0.0006 per 1K tokens
        input_cost = (total_input_tokens / 1000) * 0.00015
        output_cost = (total_output_tokens / 1000) * 0.0006
        estimated_cost = input_cost + output_cost
        
        return {
            'totalInputTokens': total_input_tokens,
            'totalOutputTokens': total_output_tokens,
            'totalTokens': total_tokens,
            'estimatedCost': f"{estimated_cost:.4f} USD"
        }

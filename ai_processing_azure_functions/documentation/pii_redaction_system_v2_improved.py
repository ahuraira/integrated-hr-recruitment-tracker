import re
import json
import uuid
from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Dict, Tuple, Any
import logging

# Required dependency for robust global phone number detection
try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    PHONENUMBERS_AVAILABLE = True
except ImportError:
    PHONENUMBERS_AVAILABLE = False
    print("WARNING: phonenumbers library not installed. Phone detection will be less accurate.")


class RedactionLevel(Enum):
    MINIMAL = "minimal"     # Only highest-sensitivity: SSNs, long IDs, credit cards
    STANDARD = "standard"   # emails, phones, names, addresses, organizations
    STRICT = "strict"       # Also job titles, schools, URLs, dates
    COMPLETE = "complete"   # Everything detectable


@dataclass
class PIIToken:
    token_id: str
    original_value: str
    pii_type: str
    sensitivity_level: int
    span: Tuple[int, int]
    confidence: float = 1.0  # Added confidence scoring


class PIIRedactionSystemV2:
    def __init__(self):
        # Enhanced patterns with Middle Eastern focus
        self.patterns = {
            # More comprehensive email pattern
            "email": re.compile(
                r'(?:[A-Za-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&\'*+/=?^_`{|}~-]+)*)'
                r'@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?',
                flags=re.IGNORECASE
            ),
            
            # Enhanced URL pattern with better domain detection
            "url": re.compile(
                r'(?:(?:https?://)?(?:www\.)?[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?'
                r'(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*'
                r'(?:\.[A-Za-z]{2,})'
                r'(?:/[^\s]*)?)',
                flags=re.IGNORECASE
            ),
            
            # Middle Eastern National ID patterns
            "uae_emirates_id": re.compile(r'\b784-\d{4}-\d{7}-\d\b'),  # UAE Emirates ID
            "saudi_national_id": re.compile(r'\b[12]\d{9}\b'),  # Saudi National ID (10 digits starting with 1 or 2)
            "kuwait_civil_id": re.compile(r'\b[12]\d{11}\b'),  # Kuwait Civil ID (12 digits)
            "qatar_id": re.compile(r'\b[23]\d{10}\b'),  # Qatar ID (11 digits starting with 2 or 3)
            "bahrain_cpr": re.compile(r'\b[12]\d{8}\b'),  # Bahrain CPR (9 digits)
            "oman_civil_id": re.compile(r'\b\d{8}\b'),  # Oman Civil ID (8 digits)
            "jordan_national_id": re.compile(r'\b[12]\d{9}\b'),  # Jordan National ID
            "lebanon_id": re.compile(r'\b\d{1,2}-\d{1,3}-\d{3}\b'),  # Lebanon ID format
            
            # Gulf-specific passport patterns
            "gulf_passport": re.compile(r'\b[A-Z]\d{7,8}\b'),  # Gulf passport format
            
            # P.O. Box patterns common in Middle East
            "po_box": re.compile(r'\bP\.?O\.?\s*Box\s+\d+\b', flags=re.IGNORECASE),
            
            # Visa and residence permit patterns
            "uae_visa": re.compile(r'\b\d{3}/\d{4}/\d{7}\b'),  # UAE visa format
            "residence_permit": re.compile(r'\bRP\s*\d{8,10}\b', flags=re.IGNORECASE),
            
            # Credit card patterns (more comprehensive)
            "credit_card": re.compile(r'\b(?:\d[ -]*){13,19}\d\b'),
            
            # Long numeric sequences (enhanced for Gulf region)
            "long_numeric_id": re.compile(r'\b\d{8,15}\b'),  # Extended range for various IDs
            
            # Date patterns (including Arabic date formats)
            "date_pattern": re.compile(r'\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|\d{1,2}\.\d{1,2}\.\d{2,4})\b'),
            
            # Gulf postal codes and area codes
            "gulf_postal": re.compile(r'\b\d{5}(?:-\d{4})?\b'),  # Standard 5-digit postal codes
            
            # Professional license patterns for Gulf countries
            "professional_license": re.compile(r'\b(?:DHA|HAAD|MOH|SCFHS|QCHP)\s*[:-]?\s*\d+\b', flags=re.IGNORECASE),
            
            # Banking IBAN patterns for GCC countries
            "iban_gcc": re.compile(r'\b(?:AE|BH|KW|OM|QA|SA)\d{2}[A-Z0-9]{4}\d{16,18}\b'),
        }

    def find_structured_pii(self, text: str) -> List[PIIToken]:
        """Enhanced structured PII detection with better global coverage"""
        tokens: List[PIIToken] = []
        seen_spans = set()

        # Apply all regex patterns
        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if self._is_overlapping_span(span, seen_spans):
                    continue
                
                seen_spans.add(span)
                tokens.append(PIIToken(
                    token_id=str(uuid.uuid4()),
                    original_value=match.group(0),
                    pii_type=pii_type,
                    sensitivity_level=self._sensitivity_for_type(pii_type),
                    span=span,
                    confidence=0.95  # High confidence for regex matches
                ))

        # Enhanced phone number detection
        phone_tokens = self._extract_phone_numbers(text, seen_spans)
        tokens.extend(phone_tokens)
        seen_spans.update(token.span for token in phone_tokens)

        # Sort tokens by start position
        tokens.sort(key=lambda t: t.span[0])
        return tokens

    def _extract_phone_numbers(self, text: str, seen_spans: set) -> List[PIIToken]:
        """Comprehensive Middle Eastern and global phone number extraction"""
        phone_tokens = []
        
        if PHONENUMBERS_AVAILABLE:
            # Priority regions for Middle Eastern countries
            middle_east_regions = ['AE', 'SA', 'KW', 'BH', 'OM', 'QA', 'JO', 'LB', 'EG', 'IR', 'IQ', 'IL', 'PS', 'SY', 'YE']
            other_regions = ['US', 'GB', 'CA', 'AU', 'IN', 'PK', 'BD', 'PH', 'MY', 'SG', None]
            
            # Try Middle Eastern regions first, then others
            all_regions = middle_east_regions + other_regions
            
            processed_numbers = set()
            
            for region in all_regions:
                try:
                    for match in phonenumbers.PhoneNumberMatcher(text, region):
                        span = (match.start, match.end)
                        if self._is_overlapping_span(span, seen_spans):
                            continue
                        
                        # Avoid duplicate processing of the same number
                        number_key = (match.start, match.end, text[match.start:match.end])
                        if number_key in processed_numbers:
                            continue
                        
                        # Validate the number
                        if phonenumbers.is_valid_number(match.number):
                            formatted_number = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164)
                            
                            # Check if it's a Middle Eastern number for higher confidence
                            region_code = phonenumbers.region_code_for_number(match.number)
                            is_middle_east = region_code in middle_east_regions
                            confidence = 0.98 if is_middle_east else 0.95
                            
                            phone_tokens.append(PIIToken(
                                token_id=str(uuid.uuid4()),
                                original_value=text[match.start:match.end],
                                pii_type="phone",
                                sensitivity_level=self._sensitivity_for_type("phone"),
                                span=span,
                                confidence=confidence
                            ))
                            seen_spans.add(span)
                            processed_numbers.add(number_key)
                            
                except Exception as e:
                    logging.debug(f"Phone detection failed for region {region}: {e}")
                    continue
                        
        else:
            # Enhanced fallback with Middle Eastern focus
            phone_tokens.extend(self._fallback_phone_detection_middle_east(text, seen_spans))
        
        return phone_tokens

    def _fallback_phone_detection_middle_east(self, text: str, seen_spans: set) -> List[PIIToken]:
        """Enhanced fallback phone number detection focused on Middle Eastern patterns"""
        phone_tokens = []
        
        # Middle Eastern phone patterns with country codes
        me_phone_patterns = [
            # UAE: +971 XX XXX XXXX
            re.compile(r'\+971[\s-]?(?:50|51|52|54|55|56|58|2|3|4|6|7|9)[\s-]?\d{3}[\s-]?\d{4}'),
            # Saudi Arabia: +966 XX XXX XXXX  
            re.compile(r'\+966[\s-]?(?:50|51|53|54|55|56|57|58|59|1[1-9])[\s-]?\d{3}[\s-]?\d{4}'),
            # Kuwait: +965 XXXX XXXX
            re.compile(r'\+965[\s-]?(?:[2469]\d{3}|5\d{3}|[17]\d{3})[\s-]?\d{4}'),
            # Qatar: +974 XXXX XXXX
            re.compile(r'\+974[\s-]?(?:[3567]\d{3}|4[04-9]\d{2}|[2489]\d{3})[\s-]?\d{4}'),
            # Bahrain: +973 XXXX XXXX
            re.compile(r'\+973[\s-]?(?:[13679]\d{3})[\s-]?\d{4}'),
            # Oman: +968 XXXX XXXX
            re.compile(r'\+968[\s-]?(?:[79]\d{3}|2[2-9]\d{2})[\s-]?\d{4}'),
            # Jordan: +962 X XXXX XXXX
            re.compile(r'\+962[\s-]?(?:[2-9])[\s-]?\d{4}[\s-]?\d{4}'),
            # Lebanon: +961 XX XXX XXX
            re.compile(r'\+961[\s-]?(?:[1-9]\d?)[\s-]?\d{3}[\s-]?\d{3}'),
            # Egypt: +20 XXX XXX XXXX
            re.compile(r'\+20[\s-]?(?:1[0125]|2)[\s-]?\d{3}[\s-]?\d{4}'),
            
            # Local formats without country codes
            # UAE local: 0XX XXX XXXX
            re.compile(r'0(?:50|51|52|54|55|56|58|2|3|4|6|7|9)[\s-]?\d{3}[\s-]?\d{4}'),
            # Saudi local: 0XX XXX XXXX
            re.compile(r'0(?:50|51|53|54|55|56|57|58|59|1[1-9])[\s-]?\d{3}[\s-]?\d{4}'),
            
            # General international format
            re.compile(r'\+\d{1,3}[\s.-]?\d{1,4}[\s.-]?\d{1,4}[\s.-]?\d{1,9}'),
            # General local format with area codes
            re.compile(r'(?:\(\d{2,4}\)|\d{2,4})[\s.-]?\d{3,4}[\s.-]?\d{3,4}'),
        ]
        
        for i, pattern in enumerate(me_phone_patterns):
            for match in pattern.finditer(text):
                span = (match.start(), match.end())
                if self._is_overlapping_span(span, seen_spans):
                    continue
                
                # Basic validation: must contain appropriate number of digits
                phone_text = match.group(0)
                digit_count = len(re.findall(r'\d', phone_text))
                
                # Middle Eastern phones typically have 8-12 digits (excluding country code)
                # With country code, total can be 10-15 digits
                if 7 <= digit_count <= 15:
                    # Higher confidence for Middle Eastern patterns (first 10 patterns)
                    confidence = 0.90 if i < 10 else 0.80
                    
                    phone_tokens.append(PIIToken(
                        token_id=str(uuid.uuid4()),
                        original_value=phone_text,
                        pii_type="phone",
                        sensitivity_level=self._sensitivity_for_type("phone"),
                        span=span,
                        confidence=confidence
                    ))
                    seen_spans.add(span)
        
        return phone_tokens

    def extract_semantic_pii_with_llm(self, text: str, llm_client: Any) -> List[PIIToken]:
        """Enhanced LLM-based semantic PII extraction with structured output and Middle Eastern focus"""
        
        enhanced_prompt = """
        You are an expert PII detection system specializing in Middle Eastern CVs. Extract ALL personally identifiable information from the CV text below.
        
        CRITICAL INSTRUCTIONS:
        1. Find EXACT substrings as they appear in the text - do not modify or reformat
        2. Pay special attention to Arabic names, Middle Eastern organizations, and regional patterns
        3. Look for these PII types: name, address, organization, school, job_title, certification_number, license_number, national_id
        4. Include all variations of names (full name, first name only, last name only, nicknames, Arabic transliterations)
        5. Detect Middle Eastern companies, universities, government entities, certification bodies
        6. Find physical addresses including Arabic address formats, P.O. Boxes, district names
        7. Identify professional titles and positions (including Arabic titles if transliterated)
        8. Look for national IDs, Emirates IDs, Saudi IDs, passport numbers, visa numbers
        9. Detect Gulf-specific certifications and professional licenses
        
        MIDDLE EASTERN SPECIFIC PATTERNS TO LOOK FOR:
        - Arabic names and their English transliterations
        - Gulf company suffixes (LLC, FZE, FZCO, WLL, etc.)
        - Regional universities (AUB, AUS, UAEU, KSU, etc.)
        - Emirates ID numbers, Saudi ID numbers, Kuwaiti civil IDs
        - P.O. Box addresses common in Gulf countries
        - Professional councils and regulatory body certifications
        
        Extract each piece of PII as an exact substring from the original text.
        """

        # Structured output schema for reliable JSON parsing
        schema = {
            "type": "object",
            "properties": {
                "pii_entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "original_value": {
                                "type": "string",
                                "description": "Exact substring from the CV text"
                            },
                            "pii_type": {
                                "type": "string",
                                "enum": ["name", "address", "organization", "school", "job_title", "certification_number", "license_number", "national_id"],
                                "description": "Type of PII detected"
                            },
                            "sensitivity_level": {
                                "type": "integer",
                                "minimum": 1,
                                "maximum": 4,
                                "description": "Sensitivity level (1=lowest, 4=highest)"
                            },
                            "all_variations": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "All variations of this entity found in text"
                            },
                            "context": {
                                "type": "string",
                                "description": "Brief context where this PII was found"
                            },
                            "region_specific": {
                                "type": "boolean",
                                "description": "True if this is Middle Eastern specific PII"
                            }
                        },
                        "required": ["original_value", "pii_type", "sensitivity_level", "all_variations", "context"]
                    }
                }
            },
            "required": ["pii_entities"]
        }

        try:
            response = llm_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise PII extraction system specializing in Middle Eastern CVs. Extract PII using the provided schema."
                    },
                    {"role": "user", "content": f"{enhanced_prompt}\n\nCV TEXT:\n{text}"}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "pii_extraction",
                        "schema": schema,
                        "strict": True
                    }
                },
                temperature=0.0,
                max_tokens=3000,
            )
            
            content = response.choices[0].message.content.strip()
            parsed_response = json.loads(content)
            entities = parsed_response.get("pii_entities", [])
            
        except Exception as e:
            logging.error(f"LLM PII extraction failed: {e}")
            # Don't fail the entire process - return empty list
            return []

        semantic_tokens = []
        processed_spans = set()
        
        for ent in entities:
            original_value = ent.get("original_value", "").strip()
            if not original_value:
                continue
                
            pii_type = ent.get("pii_type", "unknown")
            sensitivity = int(ent.get("sensitivity_level", 3))
            
            # Find all occurrences of this value (case-sensitive first, then case-insensitive)
            positions = []
            
            # Try exact match first
            start = 0
            while True:
                pos = text.find(original_value, start)
                if pos == -1:
                    break
                positions.append((pos, pos + len(original_value)))
                start = pos + 1
            
            # If no exact matches, try case-insensitive
            if not positions:
                start = 0
                while True:
                    pos = text.lower().find(original_value.lower(), start)
                    if pos == -1:
                        break
                    # Use the actual case from the text
                    actual_value = text[pos:pos + len(original_value)]
                    positions.append((pos, pos + len(actual_value)))
                    start = pos + 1
            
            # Create tokens for all found positions
            for span in positions:
                if span in processed_spans:
                    continue
                    
                processed_spans.add(span)
                semantic_tokens.append(PIIToken(
                    token_id=str(uuid.uuid4()),
                    original_value=text[span[0]:span[1]],
                    pii_type=pii_type,
                    sensitivity_level=sensitivity,
                    span=span,
                    confidence=0.90  # High confidence for LLM detection
                ))

        semantic_tokens.sort(key=lambda t: t.span[0])
        return semantic_tokens

    def create_redacted_text(
        self,
        text: str,
        llm_client: Any,  # Made mandatory - no Optional
        redaction_level: RedactionLevel = RedactionLevel.STANDARD
    ) -> Dict[str, Any]:
        """
        Main entry point - LLM client is now mandatory for comprehensive PII detection
        """
        if llm_client is None:
            raise ValueError("LLM client is required for comprehensive PII detection")
        
        # Step 1: Find structured PII
        structured_tokens = self.find_structured_pii(text)
        
        # Step 2: Find semantic PII (mandatory)
        semantic_tokens = self.extract_semantic_pii_with_llm(text, llm_client)
        
        # Step 3: Merge tokens with smart overlap resolution
        merged_tokens = self._merge_tokens_smart(structured_tokens, semantic_tokens)
        
        # Step 4: Filter by redaction level
        threshold = self._threshold_for_level(redaction_level)
        tokens_to_redact = [t for t in merged_tokens if t.sensitivity_level >= threshold]
        
        # Step 5: Create deterministic placeholders and mapping
        mapping = {}
        replacements = []
        
        for i, token in enumerate(tokens_to_redact, start=1):
            placeholder = f"[PII_{token.pii_type.upper()}_{i:03d}]"
            mapping[placeholder] = {
                "original_value": token.original_value,
                "pii_type": token.pii_type,
                "sensitivity_level": token.sensitivity_level,
                "confidence": token.confidence
            }
            replacements.append((token.span[0], token.span[1], placeholder))
        
        # Step 6: Apply replacements
        redacted_text = self._apply_span_replacements(text, replacements)
        
        # Step 7: Quality metrics
        quality_metrics = {
            "total_pii_detected": len(merged_tokens),
            "pii_redacted": len(tokens_to_redact),
            "structured_pii_count": len(structured_tokens),
            "semantic_pii_count": len(semantic_tokens),
            "average_confidence": sum(t.confidence for t in tokens_to_redact) / len(tokens_to_redact) if tokens_to_redact else 0,
            "redaction_coverage": len(tokens_to_redact) / len(merged_tokens) if merged_tokens else 0
        }
        
        return {
            "redacted_text": redacted_text,
            "mapping": mapping,
            "tokens": [asdict(t) for t in tokens_to_redact],
            "quality_metrics": quality_metrics
        }

    # Enhanced helper methods
    def _merge_tokens_smart(self, structured: List[PIIToken], semantic: List[PIIToken]) -> List[PIIToken]:
        """Smart token merging with better overlap resolution"""
        all_tokens = structured + semantic
        all_tokens.sort(key=lambda t: t.span[0])
        
        merged = []
        for token in all_tokens:
            # Check for overlaps with existing merged tokens
            overlapped = False
            for i, existing in enumerate(merged):
                if self._spans_overlap(token.span, existing.span):
                    # Prefer higher confidence, then structured over semantic
                    if (token.confidence > existing.confidence or 
                        (token.confidence == existing.confidence and token in structured)):
                        merged[i] = token
                    overlapped = True
                    break
            
            if not overlapped:
                merged.append(token)
        
        merged.sort(key=lambda t: t.span[0])
        return merged

    def _sensitivity_for_type(self, pii_type: str) -> int:
        """Enhanced sensitivity mapping with Middle Eastern focus"""
        sensitivity_map = {
            # Highest sensitivity (4) - Critical PII
            "uae_emirates_id": 4,
            "saudi_national_id": 4,
            "kuwait_civil_id": 4,
            "qatar_id": 4,
            "bahrain_cpr": 4,
            "oman_civil_id": 4,
            "jordan_national_id": 4,
            "lebanon_id": 4,
            "gulf_passport": 4,
            "credit_card": 4,
            "iban_gcc": 4,
            "national_id": 4,
            
            # High sensitivity (3) - Personal information
            "email": 3,
            "phone": 3,
            "name": 3,
            "address": 3,
            "date_pattern": 3,
            "long_numeric_id": 3,
            "uae_visa": 3,
            "residence_permit": 3,
            "professional_license": 3,
            "certification_number": 3,
            "license_number": 3,
            
            # Medium sensitivity (2) - Professional information
            "url": 2,
            "organization": 2,
            "school": 2,
            "po_box": 2,
            "gulf_postal": 2,
            
            # Lower sensitivity (1) - General information
            "job_title": 1,
        }
        return sensitivity_map.get(pii_type, 2)

    def _threshold_for_level(self, level: RedactionLevel) -> int:
        """Enhanced redaction level thresholds"""
        thresholds = {
            RedactionLevel.MINIMAL: 4,    # Only critical PII
            RedactionLevel.STANDARD: 3,   # High and critical PII
            RedactionLevel.STRICT: 2,     # Medium, high, and critical PII  
            RedactionLevel.COMPLETE: 1    # All detectable PII
        }
        return thresholds[level]

    def _is_overlapping_span(self, span: Tuple[int, int], seen_spans: set) -> bool:
        """Check if span overlaps with any in seen_spans"""
        for seen_span in seen_spans:
            if self._spans_overlap(span, seen_span):
                return True
        return False

    @staticmethod
    def _spans_overlap(a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        """Check if two spans overlap"""
        return not (a[1] <= b[0] or b[1] <= a[0])

    @staticmethod
    def _apply_span_replacements(text: str, replacements: List[Tuple[int, int, str]]) -> str:
        """Apply span-based replacements efficiently"""
        if not replacements:
            return text
        
        # Sort by start position and validate non-overlap
        replacements_sorted = sorted(replacements, key=lambda r: r[0])
        
        # Build result by processing from end to start
        result_parts = []
        current_pos = len(text)
        
        for start, end, replacement in reversed(replacements_sorted):
            result_parts.append(text[end:current_pos])
            result_parts.append(replacement)
            current_pos = start
        
        result_parts.append(text[:current_pos])
        
        return ''.join(reversed(result_parts))


def main():
    """Test the enhanced Middle Eastern redaction system"""
    sample_cv = """
    أحمد محمد العلي (Ahmed Mohammed Al-Ali)
    Senior Software Engineer | مهندس برمجيات أول
    Email: ahmed.alali@techcompany.ae / a.alali@gmail.com
    Phone: +971 50 123 4567 (UAE) / +966 55 987 6543 (KSA)
    WhatsApp: +971 56 789 1234
    LinkedIn: https://www.linkedin.com/in/ahmedali-uae
    Emirates ID: 784-1985-1234567-8
    Passport: A1234567 (UAE)
    
    ADDRESS:
    Villa 123, Street 45, Al Wasl Area
    P.O. Box 12345, Dubai, UAE
    
    PROFESSIONAL EXPERIENCE:
    Senior Software Engineer - Emirates NBD Bank (2021-Present)
    Software Developer - Dubai Internet City, Microsoft Gulf FZE (2019-2021)
    Junior Developer - Emaar Properties PJSC (2017-2019)
    
    EDUCATION:
    Master of Computer Science - American University of Sharjah (AUS) - 2017
    Bachelor of Engineering - UAE University (UAEU) - 2015
    
    CERTIFICATIONS:
    DHA License: DHA-12345678 (Dubai Health Authority)
    PMP Certification: PMI-987654321
    AWS Solutions Architect: AWS-SA-123456789
    
    BANKING DETAILS:
    IBAN: AE070331234567890123456
    Account: 1234567890 (Emirates NBD)
    
    PERSONAL:
    Date of Birth: 15/03/1990
    Nationality: Emirati
    Visa Status: UAE National
    Saudi ID (Iqama): 2123456789 (for KSA projects)
    Kuwait Civil ID: 290123456789 (previous residence)
    
    EMERGENCY CONTACT:
    Fatima Al-Ali (Wife): +971 50 888 9999
    Mohammed Al-Ali (Father): +971 4 234 5678
    
    REFERENCES:
    Dr. Khalid Al-Mansoori, CTO, Etisalat Group
    Email: k.almansoori@etisalat.ae
    Phone: +971 2 345 6789
    
    Eng. Sarah Al-Zahra, Director, Dubai Municipality
    Phone: +971 4 567 8901
    """
    
    # Mock LLM client with structured output for testing
    # Replace this with your actual Azure OpenAI or other LLM client
    class MockStructuredLLMClient:
        class ChatCompletions:
            def create(self, **kwargs):
                # Mock structured response focusing on Middle Eastern PII
                mock_response = {
                    "pii_entities": [
                        {
                            "original_value": "أحمد محمد العلي",
                            "pii_type": "name",
                            "sensitivity_level": 4,
                            "all_variations": ["أحمد محمد العلي", "Ahmed Mohammed Al-Ali", "Ahmed Al-Ali"],
                            "context": "candidate name in Arabic and English",
                            "region_specific": True
                        },
                        {
                            "original_value": "Ahmed Mohammed Al-Ali",
                            "pii_type": "name",
                            "sensitivity_level": 4,
                            "all_variations": ["Ahmed Mohammed Al-Ali", "Ahmed Al-Ali"],
                            "context": "candidate name transliteration",
                            "region_specific": True
                        },
                        {
                            "original_value": "Emirates NBD Bank",
                            "pii_type": "organization",
                            "sensitivity_level": 2,
                            "all_variations": ["Emirates NBD Bank", "Emirates NBD"],
                            "context": "current employer",
                            "region_specific": True
                        },
                        {
                            "original_value": "American University of Sharjah",
                            "pii_type": "school",
                            "sensitivity_level": 2,
                            "all_variations": ["American University of Sharjah", "AUS"],
                            "context": "university education",
                            "region_specific": True
                        },
                        {
                            "original_value": "Villa 123, Street 45, Al Wasl Area",
                            "pii_type": "address",
                            "sensitivity_level": 3,
                            "all_variations": ["Villa 123, Street 45, Al Wasl Area"],
                            "context": "residential address",
                            "region_specific": True
                        },
                        {
                            "original_value": "Dr. Khalid Al-Mansoori",
                            "pii_type": "name",
                            "sensitivity_level": 4,
                            "all_variations": ["Dr. Khalid Al-Mansoori", "Khalid Al-Mansoori"],
                            "context": "reference contact",
                            "region_specific": True
                        },
                        {
                            "original_value": "Fatima Al-Ali",
                            "pii_type": "name",
                            "sensitivity_level": 4,
                            "all_variations": ["Fatima Al-Ali"],
                            "context": "emergency contact",
                            "region_specific": True
                        }
                    ]
                }
                
                class MockChoice:
                    def __init__(self, content):
                        self.message = type('obj', (object,), {'content': json.dumps(content)})
                        
                return type('obj', (object,), {
                    'choices': [MockChoice(mock_response)]
                })
        
        def __init__(self):
            self.chat = type('obj', (object,), {'completions': self.ChatCompletions()})
    
    # Initialize system
    redactor = PIIRedactionSystemV2()
    mock_client = MockStructuredLLMClient()  # Replace with your actual LLM client
    
    print("=== ORIGINAL CV (Middle Eastern Sample) ===")
    print(sample_cv)
    print("\n" + "="*80)
    
    # Process CV with different redaction levels
    for level in [RedactionLevel.STANDARD, RedactionLevel.STRICT]:
        print(f"\n=== REDACTION LEVEL: {level.value.upper()} ===")
        
        result = redactor.create_redacted_text(
            sample_cv,
            llm_client=mock_client,
            redaction_level=level
        )
        
        print("REDACTED CV:")
        print("-" * 40)
        print(result["redacted_text"])
        
        print(f"\nQUALITY METRICS:")
        print("-" * 20)
        for key, value in result["quality_metrics"].items():
            print(f"{key}: {value}")
        
        print(f"\nDETECTED PII BREAKDOWN:")
        print("-" * 25)
        pii_types = {}
        for token in result['tokens']:
            pii_type = token['pii_type']
            pii_types[pii_type] = pii_types.get(pii_type, 0) + 1
        
        for pii_type, count in sorted(pii_types.items()):
            print(f"- {pii_type}: {count} instances")
        
        print("\n" + "="*80)
    
    # Show some examples of detected patterns
    print("\nEXAMPLES OF MIDDLE EASTERN PATTERNS DETECTED:")
    print("-" * 50)
    
    # Test individual patterns
    test_patterns = {
        "Emirates ID": "784-1985-1234567-8",
        "Saudi ID": "2123456789", 
        "UAE Phone": "+971 50 123 4567",
        "Saudi Phone": "+966 55 987 6543",
        "UAE IBAN": "AE070331234567890123456",
        "P.O. Box": "P.O. Box 12345",
        "DHA License": "DHA-12345678"
    }
    
    for pattern_name, example in test_patterns.items():
        tokens = redactor.find_structured_pii(example)
        if tokens:
            print(f"✓ {pattern_name}: '{example}' -> detected as {tokens[0].pii_type} (confidence: {tokens[0].confidence:.2f})")
        else:
            print(f"✗ {pattern_name}: '{example}' -> not detected")


if __name__ == "__main__":
    main()
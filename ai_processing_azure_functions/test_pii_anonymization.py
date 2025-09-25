"""
Specialized PII and Anonymization Test Suite
AI-Powered CV Processing Engine for TTE Recruitment Suite

This test suite focuses specifically on PII identification and anonymization
functionality, including edge cases, multilingual content, and privacy compliance.

Version: 1.0
Date: September 24, 2025
"""

import pytest
import json
import os
from unittest.mock import Mock, patch
from typing import Dict, Any, List

from shared_code.candidate_data_service import CandidateDataService
from test_utilities import TestDataGenerator, MockResponseGenerator, ValidationHelpers

class TestPIIIdentification:
    """Test cases for PII identification functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = CandidateDataService()
    
    def test_basic_pii_identification(self):
        """Test identification of basic PII types"""
        cv_content = """
        John Smith
        Email: john.smith@email.com
        Phone: +1-555-123-4567
        Address: 123 Main Street, New York, NY 10001
        Company: Tech Innovations Inc
        University: Stanford University
        """
        
        expected_pii_types = ['name', 'organization', 'school']
        
        # Mock the AI service response
        mock_pii_entities = [
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            },
            {
                "original_value": "Tech Innovations Inc",
                "pii_type": "organization", 
                "sensitivity_level": 2,
                "all_variations": ["Tech Innovations Inc"],
                "context": "current employer",
                "region_specific": False
            },
            {
                "original_value": "Stanford University",
                "pii_type": "school",
                "sensitivity_level": 2,
                "all_variations": ["Stanford University"],
                "context": "education",
                "region_specific": False
            }
        ]
        
        with patch.object(self.service.openai_service, 'call_assistant') as mock_call:
            mock_response = Mock()
            mock_response.content = json.dumps({"pii_entities": mock_pii_entities})
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 100
            mock_response.usage.completion_tokens = 50
            mock_call.return_value = mock_response
            
            with patch.object(self.service.openai_service, 'get_assistant_id', return_value="asst_test"):
                pii_data, anonymized_content, log = self.service._identify_and_anonymize_pii(cv_content)
        
        # Verify all expected PII types were identified
        identified_types = [entity['pii_type'] for entity in pii_data['pii_entities']]
        for expected_type in expected_pii_types:
            assert expected_type in identified_types
    
    def test_multilingual_pii_identification(self):
        """Test PII identification in multilingual content"""
        cv_content = TestDataGenerator.create_multilingual_cv_content()
        
        expected_entities = [
            {
                "original_value": "محمد أحمد",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["محمد أحمد", "Mohammed Ahmed"],
                "context": "candidate name in Arabic and English",
                "region_specific": True
            },
            {
                "original_value": "784-1985-1234567-8",
                "pii_type": "national_id",
                "sensitivity_level": 4,
                "all_variations": ["784-1985-1234567-8"],
                "context": "Emirates ID number",
                "region_specific": True
            },
            {
                "original_value": "American University of Sharjah",
                "pii_type": "school",
                "sensitivity_level": 2,
                "all_variations": ["American University of Sharjah", "الجامعة الأمريكية في الشارقة"],
                "context": "university in English and Arabic",
                "region_specific": True
            }
        ]
        
        with patch.object(self.service.openai_service, 'call_assistant') as mock_call:
            mock_response = Mock()
            mock_response.content = json.dumps({"pii_entities": expected_entities})
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 150
            mock_response.usage.completion_tokens = 75
            mock_call.return_value = mock_response
            
            with patch.object(self.service.openai_service, 'get_assistant_id', return_value="asst_test"):
                pii_data, anonymized_content, log = self.service._identify_and_anonymize_pii(cv_content)
        
        # Verify multilingual and region-specific PII was identified
        region_specific_entities = [e for e in pii_data['pii_entities'] if e.get('region_specific', False)]
        assert len(region_specific_entities) >= 2
        
        # Verify Arabic text was identified
        arabic_entities = [e for e in pii_data['pii_entities'] 
                          if any('ا' in variation for variation in e['all_variations'])]
        assert len(arabic_entities) >= 1
    
    def test_complex_pii_scenarios(self):
        """Test identification of complex PII scenarios"""
        cv_content = TestDataGenerator.create_complex_pii_cv()
        
        # Mock response for complex PII
        complex_pii_entities = [
            {
                "original_value": "Dr. John Michael Smith Jr.",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["Dr. John Michael Smith Jr.", "John Michael Smith Jr.", "John Smith", "Dr. Smith"],
                "context": "full name with title and suffix",
                "region_specific": False
            },
            {
                "original_value": "123-45-6789",
                "pii_type": "national_id", 
                "sensitivity_level": 4,
                "all_variations": ["123-45-6789"],
                "context": "Social Security Number",
                "region_specific": True
            },
            {
                "original_value": "D123456789",
                "pii_type": "license_number",
                "sensitivity_level": 3,
                "all_variations": ["D123456789"],
                "context": "Driver's License Number",
                "region_specific": True
            },
            {
                "original_value": "123 Tech Street, San Francisco, CA 94105",
                "pii_type": "address",
                "sensitivity_level": 3,
                "all_variations": ["123 Tech Street, San Francisco, CA 94105", "123 Tech Street"],
                "context": "full residential address",
                "region_specific": False
            }
        ]
        
        with patch.object(self.service.openai_service, 'call_assistant') as mock_call:
            mock_response = Mock()
            mock_response.content = json.dumps({"pii_entities": complex_pii_entities})
            mock_response.usage = Mock()
            mock_response.usage.prompt_tokens = 200
            mock_response.usage.completion_tokens = 100
            mock_call.return_value = mock_response
            
            with patch.object(self.service.openai_service, 'get_assistant_id', return_value="asst_test"):
                pii_data, anonymized_content, log = self.service._identify_and_anonymize_pii(cv_content)
        
        # Verify high-sensitivity PII was identified
        high_sensitivity_entities = [e for e in pii_data['pii_entities'] if e['sensitivity_level'] >= 4]
        assert len(high_sensitivity_entities) >= 2
        
        # Verify national ID types were identified
        national_id_entities = [e for e in pii_data['pii_entities'] if e['pii_type'] == 'national_id']
        assert len(national_id_entities) >= 1
    
    def test_pii_entity_validation(self):
        """Test validation of PII entity structures"""
        valid_entity = {
            "original_value": "John Smith",
            "pii_type": "name",
            "sensitivity_level": 4,
            "all_variations": ["John Smith", "John"],
            "context": "candidate name",
            "region_specific": False
        }
        
        invalid_entities = [
            # Missing required field
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"]
                # Missing 'context'
            },
            # Invalid sensitivity level
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 5,  # Invalid (should be 1-4)
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            },
            # Invalid PII type
            {
                "original_value": "John Smith",
                "pii_type": "invalid_type",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            }
        ]
        
        # Valid entity should pass validation
        assert ValidationHelpers.validate_pii_entity_structure(valid_entity) is True
        
        # Invalid entities should fail validation
        for invalid_entity in invalid_entities:
            assert ValidationHelpers.validate_pii_entity_structure(invalid_entity) is False

class TestAnonymization:
    """Test cases for PII anonymization functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.service = CandidateDataService()
    
    def test_deterministic_placeholder_generation(self):
        """Test that placeholders are generated deterministically"""
        pii_entities = [
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            },
            {
                "original_value": "Tech Corp",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["Tech Corp"],
                "context": "company name",
                "region_specific": False
            },
            {
                "original_value": "Stanford University",
                "pii_type": "school",
                "sensitivity_level": 2,
                "all_variations": ["Stanford University"],
                "context": "university",
                "region_specific": False
            }
        ]
        
        original_content = "John Smith works at Tech Corp and studied at Stanford University."
        
        # Run anonymization multiple times
        anonymized_1 = self.service._create_anonymized_content(original_content, pii_entities)
        anonymized_2 = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Results should be identical (deterministic)
        assert anonymized_1 == anonymized_2
        assert "[CANDIDATE_NAME]" in anonymized_1
        assert "[COMPANY_1]" in anonymized_1
        assert "[UNIVERSITY_1]" in anonymized_1
    
    def test_multiple_entity_instances(self):
        """Test anonymization with multiple instances of same entity type"""
        pii_entities = [
            {
                "original_value": "Google",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["Google"],
                "context": "company 1",
                "region_specific": False
            },
            {
                "original_value": "Microsoft",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["Microsoft"],
                "context": "company 2",
                "region_specific": False
            },
            {
                "original_value": "Apple",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["Apple"],
                "context": "company 3",
                "region_specific": False
            }
        ]
        
        original_content = "Worked at Google, then Microsoft, and finally Apple."
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Should have different placeholders for each company
        assert "[COMPANY_1]" in anonymized
        assert "[COMPANY_2]" in anonymized
        assert "[COMPANY_3]" in anonymized
        
        # Original company names should be removed
        assert "Google" not in anonymized
        assert "Microsoft" not in anonymized
        assert "Apple" not in anonymized
    
    def test_overlapping_entity_variations(self):
        """Test anonymization with overlapping entity variations"""
        pii_entities = [
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith", "John", "Smith"],
                "context": "full name",
                "region_specific": False
            },
            {
                "original_value": "John Doe",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Doe"],
                "context": "reference name",
                "region_specific": False
            }
        ]
        
        original_content = "John Smith and John Doe are colleagues. John is experienced and Smith is skilled."
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # All variations should be replaced
        assert "John Smith" not in anonymized
        assert "John Doe" not in anonymized
        
        # Should have appropriate placeholders
        assert "[CANDIDATE_NAME]" in anonymized
    
    def test_preservation_of_document_structure(self):
        """Test that document structure is preserved during anonymization"""
        pii_entities = [
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            }
        ]
        
        original_content = """
# John Smith
## Senior Software Engineer

**Contact Information:**
- Name: John Smith
- Email: john.smith@email.com

### Experience
John Smith has 8 years of experience.

### Education
John Smith graduated from MIT.
        """
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Structure should be preserved
        assert "# [CANDIDATE_NAME]" in anonymized
        assert "## Senior Software Engineer" in anonymized
        assert "**Contact Information:**" in anonymized
        assert "- Name: [CANDIDATE_NAME]" in anonymized
        assert "### Experience" in anonymized
        assert "### Education" in anonymized
        
        # Formatting should be maintained
        assert anonymized.count("\n") == original_content.count("\n")
    
    def test_edge_case_replacements(self):
        """Test anonymization edge cases"""
        pii_entities = [
            {
                "original_value": "O'Connor",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["O'Connor", "O'Connor"],
                "context": "name with apostrophe",
                "region_specific": False
            },
            {
                "original_value": "Smith-Johnson",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["Smith-Johnson"],
                "context": "hyphenated name",
                "region_specific": False
            },
            {
                "original_value": "AT&T",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["AT&T", "AT & T"],
                "context": "company with ampersand",
                "region_specific": False
            }
        ]
        
        original_content = "Michael O'Connor and Sarah Smith-Johnson worked at AT&T. O'Connor led the team."
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Special characters should be handled correctly
        assert "O'Connor" not in anonymized
        assert "Smith-Johnson" not in anonymized
        assert "AT&T" not in anonymized
        assert "[CANDIDATE_NAME]" in anonymized
        assert "[COMPANY_1]" in anonymized
    
    def test_length_based_replacement_order(self):
        """Test that longer entities are replaced first to prevent partial replacements"""
        pii_entities = [
            {
                "original_value": "John",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John"],
                "context": "first name",
                "region_specific": False
            },
            {
                "original_value": "John Smith Corporation",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["John Smith Corporation"],
                "context": "company name",
                "region_specific": False
            }
        ]
        
        original_content = "John works at John Smith Corporation founded by John."
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Should not have partial replacements like "[CANDIDATE_NAME] Smith Corporation"
        assert "Smith Corporation" not in anonymized
        assert "[COMPANY_1]" in anonymized
        assert anonymized.count("[CANDIDATE_NAME]") == 2  # Two instances of "John"
    
    def test_complete_pii_removal_verification(self):
        """Test that all PII is completely removed from anonymized content"""
        pii_entities = [
            {
                "original_value": "Confidential Corp",
                "pii_type": "organization",
                "sensitivity_level": 4,
                "all_variations": ["Confidential Corp", "Confidential Corporation", "ConfCorp"],
                "context": "sensitive company",
                "region_specific": False
            }
        ]
        
        original_content = """
        Worked at Confidential Corp for 5 years. 
        Confidential Corporation was a great place to work.
        At ConfCorp, I learned many skills.
        """
        
        anonymized = self.service._create_anonymized_content(original_content, pii_entities)
        
        # Verify complete removal of all variations
        for entity in pii_entities:
            for variation in entity['all_variations']:
                assert variation not in anonymized
        
        # Verify placeholders are present
        assert "[COMPANY_1]" in anonymized
        assert anonymized.count("[COMPANY_1]") == 3

class TestPIIComplianceAndSecurity:
    """Test cases for PII compliance and security measures"""
    
    def test_high_sensitivity_pii_handling(self):
        """Test handling of high-sensitivity PII (level 4)"""
        high_sensitivity_entities = [
            {
                "original_value": "123-45-6789",
                "pii_type": "national_id",
                "sensitivity_level": 4,
                "all_variations": ["123-45-6789"],
                "context": "SSN",
                "region_specific": True
            },
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            }
        ]
        
        original_content = "John Smith's SSN is 123-45-6789."
        
        service = CandidateDataService()
        anonymized = service._create_anonymized_content(original_content, high_sensitivity_entities)
        
        # High-sensitivity PII should be completely removed
        assert "123-45-6789" not in anonymized
        assert "John Smith" not in anonymized
        
        # Should have appropriate high-security placeholders
        assert "[CANDIDATE_NAME]" in anonymized
        assert "[NATIONAL_ID_1]" in anonymized
    
    def test_region_specific_pii_handling(self):
        """Test handling of region-specific PII"""
        region_specific_entities = [
            {
                "original_value": "784-1985-1234567-8",
                "pii_type": "national_id",
                "sensitivity_level": 4,
                "all_variations": ["784-1985-1234567-8"],
                "context": "Emirates ID",
                "region_specific": True
            },
            {
                "original_value": "+971-50-123-4567",
                "pii_type": "phone",
                "sensitivity_level": 3,
                "all_variations": ["+971-50-123-4567", "0501234567"],
                "context": "UAE phone number",
                "region_specific": True
            }
        ]
        
        original_content = "Emirates ID: 784-1985-1234567-8, Phone: +971-50-123-4567"
        
        service = CandidateDataService()
        anonymized = service._create_anonymized_content(original_content, region_specific_entities)
        
        # Region-specific identifiers should be anonymized
        assert "784-1985-1234567-8" not in anonymized
        assert "+971-50-123-4567" not in anonymized
        assert "[NATIONAL_ID_1]" in anonymized
    
    def test_anonymization_reversibility_prevention(self):
        """Test that anonymization is not easily reversible"""
        pii_entities = [
            {
                "original_value": "Unique Company Name Inc",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["Unique Company Name Inc"],
                "context": "very specific company name",
                "region_specific": False
            }
        ]
        
        original_content = "I worked at Unique Company Name Inc for 3 years."
        
        service = CandidateDataService()
        anonymized = service._create_anonymized_content(original_content, pii_entities)
        
        # Original content should not be recoverable from anonymized version
        assert "Unique Company Name Inc" not in anonymized
        assert len(anonymized) < len(original_content)  # Placeholder is shorter
        
        # Placeholder should not reveal information about original
        assert "Unique" not in anonymized
        assert "Company" not in anonymized
        assert "Name" not in anonymized

class TestAnonymizationQualityAssurance:
    """Test cases for anonymization quality and accuracy"""
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_API_VERSION': '2024-02-01',
        'CV_DATA_EXTRACTOR_ASSISTANT_ID': 'test-extractor-id',
        'CV_PII_IDENTIFIER_ASSISTANT_ID': 'test-pii-id',
        'CV_SKILLS_ANALYST_ASSISTANT_ID': 'test-skills-id'
    })
    def test_anonymization_completeness(self):
        """Test that anonymization is complete and thorough"""
        comprehensive_pii = [
            {
                "original_value": "Dr. Sarah Michelle Johnson-Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": [
                    "Dr. Sarah Michelle Johnson-Smith",
                    "Sarah Michelle Johnson-Smith", 
                    "Sarah Johnson-Smith",
                    "Dr. Johnson-Smith",
                    "Sarah",
                    "Johnson-Smith"
                ],
                "context": "complex name with title",
                "region_specific": False
            }
        ]
        
        original_content = """
        Dr. Sarah Michelle Johnson-Smith is a senior engineer.
        Sarah has extensive experience. Johnson-Smith led multiple projects.
        Dr. Johnson-Smith received awards. Sarah Michelle Johnson-Smith graduated in 2015.
        """
        
        service = CandidateDataService()
        anonymized = service._create_anonymized_content(original_content, comprehensive_pii)
        
        # Verify all variations are removed
        variations_to_check = [
            "Dr. Sarah Michelle Johnson-Smith",
            "Sarah Michelle Johnson-Smith",
            "Sarah Johnson-Smith", 
            "Dr. Johnson-Smith",
            "Sarah",
            "Johnson-Smith"
        ]
        
        for variation in variations_to_check:
            assert variation not in anonymized
        
        # Should have consistent placeholder usage
        assert "[CANDIDATE_NAME]" in anonymized
        # Count should be reasonable (some variations might overlap)
        # The exact count can vary based on replacement order and overlaps
        placeholder_count = anonymized.count("[CANDIDATE_NAME]")
        assert placeholder_count >= 4  # At least 4 instances should be replaced
        assert placeholder_count <= len(variations_to_check)  # Not more than expected
    
    @patch.dict(os.environ, {
        'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-key',
        'AZURE_OPENAI_API_VERSION': '2024-02-01',
        'CV_DATA_EXTRACTOR_ASSISTANT_ID': 'test-extractor-id',
        'CV_PII_IDENTIFIER_ASSISTANT_ID': 'test-pii-id',
        'CV_SKILLS_ANALYST_ASSISTANT_ID': 'test-skills-id'
    })
    def test_context_preservation(self):
        """Test that meaningful context is preserved after anonymization"""
        pii_entities = [
            {
                "original_value": "John Smith",
                "pii_type": "name",
                "sensitivity_level": 4,
                "all_variations": ["John Smith"],
                "context": "candidate name",
                "region_specific": False
            },
            {
                "original_value": "TechCorp Inc",
                "pii_type": "organization",
                "sensitivity_level": 2,
                "all_variations": ["TechCorp Inc"],
                "context": "employer",
                "region_specific": False
            }
        ]
        
        original_content = """
        John Smith is a Senior Software Engineer with 8 years of experience.
        At TechCorp Inc, John Smith led a team of 10 developers and 
        delivered 15 successful projects. The candidate has strong skills
        in Python, JavaScript, and cloud architecture.
        """
        
        service = CandidateDataService()
        anonymized = service._create_anonymized_content(original_content, pii_entities)
        
        # Technical content should be preserved
        preserved_content = [
            "Senior Software Engineer",
            "8 years of experience",
            "led a team of 10 developers",
            "delivered 15 successful projects",
            "strong skills",
            "Python, JavaScript, and cloud architecture"
        ]
        
        for content in preserved_content:
            assert content in anonymized
        
        # Structure and professional context should remain
        assert "candidate" in anonymized.lower()
        assert "experience" in anonymized.lower()
        assert "skills" in anonymized.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

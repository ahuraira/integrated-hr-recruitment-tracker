#!/usr/bin/env python3
"""
Test Runner Script for CV Processing Engine
AI-Powered CV Processing Engine for TTE Recruitment Suite

This script provides different test execution modes and configurations
for comprehensive testing of the CV processing system.

Version: 1.0
Date: September 24, 2025
"""

import os
import sys
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

def setup_test_environment():
    """Setup test environment variables"""
    test_env = {
        'AZURE_OPENAI_ENDPOINT': 'https://test-openai.openai.azure.com/',
        'AZURE_OPENAI_API_KEY': 'test-api-key-12345',
        'AZURE_OPENAI_API_VERSION': '2024-02-15-preview',
        'CV_DATA_EXTRACTOR_ASSISTANT_ID': 'asst_cv_data_extractor_test',
        'CV_PII_IDENTIFIER_ASSISTANT_ID': 'asst_pii_identifier_test',
        'CV_SKILLS_ANALYST_ASSISTANT_ID': 'asst_skills_analyst_test',
        'PYTHONPATH': os.getcwd()
    }
    
    for key, value in test_env.items():
        os.environ[key] = value

def create_reports_directory():
    """Create reports directory if it doesn't exist"""
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

def run_unit_tests():
    """Run unit tests only"""
    print("🧪 Running Unit Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_cv_processing.py::TestDocumentProcessor',
        'test_cv_processing.py::TestCandidateDataService',
        'test_cv_processing.py::TestOpenAIService',
        'test_cv_processing.py::TestAICallLogger',
        '-v', '--tb=short',
        '-m', 'unit'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_integration_tests():
    """Run integration tests"""
    print("🔗 Running Integration Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_cv_processing.py::TestFullIntegration',
        '-v', '--tb=short',
        '-m', 'integration'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_pii_tests():
    """Run PII and anonymization tests"""
    print("🔒 Running PII and Anonymization Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_pii_anonymization.py',
        '-v', '--tb=short',
        '-m', 'pii'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_error_handling_tests():
    """Run error handling tests"""
    print("⚠️ Running Error Handling Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_cv_processing.py::TestErrorHandling',
        '-v', '--tb=short',
        '-m', 'error'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_performance_tests():
    """Run performance tests"""
    print("⚡ Running Performance Tests...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_cv_processing.py::TestPerformance',
        '-v', '--tb=short',
        '-m', 'performance',
        '--benchmark-only'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_all_tests_with_coverage():
    """Run all tests with coverage reporting"""
    print("🎯 Running All Tests with Coverage...")
    cmd = [
        sys.executable, '-m', 'pytest',
        'test_cv_processing.py',
        'test_pii_anonymization.py',
        '--cov=shared_code',
        '--cov-report=html:reports/htmlcov',
        '--cov-report=term-missing',
        '--cov-report=xml:reports/coverage.xml',
        '--html=reports/pytest_report.html',
        '--self-contained-html',
        '--junitxml=reports/junit.xml',
        '--json-report',
        '--json-report-file=reports/report.json',
        '-v'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_specific_test(test_pattern):
    """Run specific test by pattern"""
    print(f"🎯 Running Specific Test: {test_pattern}")
    cmd = [
        sys.executable, '-m', 'pytest',
        '-k', test_pattern,
        '-v', '--tb=short'
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def run_smoke_tests():
    """Run smoke tests for quick validation"""
    print("💨 Running Smoke Tests...")
    smoke_tests = [
        'test_cv_processing.py::TestDocumentProcessor::test_extract_markdown_from_pdf_success',
        'test_cv_processing.py::TestCandidateDataService::test_regex_extraction',
        'test_pii_anonymization.py::TestAnonymization::test_deterministic_placeholder_generation'
    ]
    
    cmd = [sys.executable, '-m', 'pytest'] + smoke_tests + ['-v', '--tb=short']
    return subprocess.run(cmd, capture_output=True, text=True)

def print_test_summary(result, test_type):
    """Print test execution summary"""
    print(f"\n{'='*60}")
    print(f"Test Type: {test_type}")
    print(f"Exit Code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ Status: PASSED")
    else:
        print("❌ Status: FAILED")
    
    # Print stdout if there's content
    if result.stdout:
        print("\n--- Test Output ---")
        print(result.stdout)
    
    # Print stderr if there are errors
    if result.stderr:
        print("\n--- Error Output ---")
        print(result.stderr)
    
    print(f"{'='*60}\n")

def validate_dependencies():
    """Validate that all required dependencies are installed"""
    print("🔍 Validating Test Dependencies...")
    
    required_packages = [
        'pytest', 'pytest-cov', 'pytest-mock', 'pytest-html',
        'responses', 'mock'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'pytest-cov':
                __import__('pytest_cov')
            elif package == 'pytest-mock':
                __import__('pytest_mock')
            elif package == 'pytest-html':
                __import__('pytest_html')
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r test-requirements.txt")
        return False
    else:
        print("✅ All test dependencies are installed")
        return True

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='CV Processing Engine Test Runner')
    parser.add_argument('--type', '-t', choices=[
        'unit', 'integration', 'pii', 'error', 'performance', 
        'all', 'smoke', 'specific'
    ], default='all', help='Type of tests to run')
    parser.add_argument('--pattern', '-p', help='Specific test pattern to run (when --type=specific)')
    parser.add_argument('--no-coverage', action='store_true', help='Skip coverage reporting')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--validate-deps', action='store_true', help='Only validate dependencies')
    
    args = parser.parse_args()
    
    # Validate dependencies first
    if not validate_dependencies():
        if args.validate_deps:
            sys.exit(1)
        print("Continuing with tests (some may fail due to missing dependencies)...")
    elif args.validate_deps:
        sys.exit(0)
    
    # Setup test environment
    setup_test_environment()
    create_reports_directory()
    
    print(f"🚀 Starting CV Processing Engine Tests")
    print(f"📅 Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Test Type: {args.type}")
    print(f"📁 Working Directory: {os.getcwd()}")
    
    # Run tests based on type
    results = []
    
    if args.type == 'unit':
        result = run_unit_tests()
        print_test_summary(result, "Unit Tests")
        results.append(('Unit Tests', result.returncode))
    
    elif args.type == 'integration':
        result = run_integration_tests()
        print_test_summary(result, "Integration Tests")
        results.append(('Integration Tests', result.returncode))
    
    elif args.type == 'pii':
        result = run_pii_tests()
        print_test_summary(result, "PII Tests")
        results.append(('PII Tests', result.returncode))
    
    elif args.type == 'error':
        result = run_error_handling_tests()
        print_test_summary(result, "Error Handling Tests")
        results.append(('Error Handling Tests', result.returncode))
    
    elif args.type == 'performance':
        result = run_performance_tests()
        print_test_summary(result, "Performance Tests")
        results.append(('Performance Tests', result.returncode))
    
    elif args.type == 'smoke':
        result = run_smoke_tests()
        print_test_summary(result, "Smoke Tests")
        results.append(('Smoke Tests', result.returncode))
    
    elif args.type == 'specific':
        if not args.pattern:
            print("❌ Error: --pattern is required when --type=specific")
            sys.exit(1)
        result = run_specific_test(args.pattern)
        print_test_summary(result, f"Specific Tests ({args.pattern})")
        results.append((f'Specific Tests ({args.pattern})', result.returncode))
    
    elif args.type == 'all':
        # Run all test types
        test_functions = [
            ('Unit Tests', run_unit_tests),
            ('Integration Tests', run_integration_tests),
            ('PII Tests', run_pii_tests),
            ('Error Handling Tests', run_error_handling_tests),
            ('Performance Tests', run_performance_tests)
        ]
        
        for test_name, test_func in test_functions:
            result = test_func()
            print_test_summary(result, test_name)
            results.append((test_name, result.returncode))
        
        # Run comprehensive coverage report
        if not args.no_coverage:
            print("📊 Generating Comprehensive Coverage Report...")
            coverage_result = run_all_tests_with_coverage()
            print_test_summary(coverage_result, "All Tests with Coverage")
    
    # Print final summary
    print("\n" + "="*80)
    print("🏁 FINAL TEST SUMMARY")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for _, code in results if code == 0)
    failed_tests = total_tests - passed_tests
    
    for test_name, exit_code in results:
        status = "✅ PASSED" if exit_code == 0 else "❌ FAILED"
        print(f"{test_name:<30} {status}")
    
    print(f"\n📈 Overall Results:")
    print(f"   Total Test Suites: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ {failed_tests} test suite(s) failed!")
        print("📋 Check the detailed output above for error details.")
        print("📁 Reports are available in the 'reports' directory.")
        sys.exit(1)
    else:
        print(f"\n✅ All {total_tests} test suite(s) passed!")
        print("🎉 CV Processing Engine is working correctly!")
        print("📁 Coverage reports are available in the 'reports' directory.")
        sys.exit(0)

if __name__ == "__main__":
    main()

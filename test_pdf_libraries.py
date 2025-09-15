#!/usr/bin/env python3
"""
PDF Text Extraction Performance Testing Tool

This script compares the performance of different PDF text extraction libraries:
- PyPDF2
- pdfplumber
- pymupdf (fitz)
- pdfminer.six
- markitdown (for markdown extraction)

Measures extraction time and memory usage for each library.
"""

import time
import tracemalloc
import gc
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import statistics

# Import libraries with error handling
libraries_available = {}

try:
    import PyPDF2
    libraries_available['pypdf2'] = True
except ImportError:
    libraries_available['pypdf2'] = False
    print("PyPDF2 not available. Install with: pip install PyPDF2")

try:
    import pdfplumber
    libraries_available['pdfplumber'] = True
except ImportError:
    libraries_available['pdfplumber'] = False
    print("pdfplumber not available. Install with: pip install pdfplumber")

try:
    import fitz  # pymupdf
    libraries_available['pymupdf'] = True
except ImportError:
    libraries_available['pymupdf'] = False
    print("PyMuPDF not available. Install with: pip install PyMuPDF")

try:
    from pdfminer.high_level import extract_text
    libraries_available['pdfminer'] = True
except ImportError:
    libraries_available['pdfminer'] = False
    print("pdfminer.six not available. Install with: pip install pdfminer.six")

try:
    from markitdown import MarkItDown
    libraries_available['markitdown'] = True
except ImportError:
    libraries_available['markitdown'] = False
    print("markitdown not available. Install with: pip install markitdown")


class PDFExtractionTester:
    def __init__(self):
        self.results = {}
        
    def extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2"""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber"""
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
    
    def extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (fitz)"""
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += page.get_text()
        doc.close()
        return text
    
    def extract_with_pdfminer(self, pdf_path: str) -> str:
        """Extract text using pdfminer.six"""
        return extract_text(pdf_path)
    
    def extract_with_markitdown(self, pdf_path: str) -> str:
        """Extract markdown using markitdown"""
        md = MarkItDown()
        result = md.convert(pdf_path)
        return result.text_content
    
    def measure_extraction(self, extraction_func, pdf_path: str, library_name: str) -> Dict:
        """Measure time and memory usage for extraction"""
        # Force garbage collection before measurement
        gc.collect()
        
        # Start memory tracking
        tracemalloc.start()
        
        # Record start time
        start_time = time.perf_counter()
        
        try:
            # Perform extraction
            text = extraction_func(pdf_path)
            
            # Record end time
            end_time = time.perf_counter()
            
            # Get memory usage
            current, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            
            # Calculate metrics
            extraction_time = end_time - start_time
            memory_mb = peak / 1024 / 1024  # Convert to MB
            text_length = len(text) if text else 0
            
            return {
                'success': True,
                'time': extraction_time,
                'memory_mb': memory_mb,
                'text_length': text_length,
                'chars_per_second': text_length / extraction_time if extraction_time > 0 else 0,
                'error': None
            }
            
        except Exception as e:
            tracemalloc.stop()
            return {
                'success': False,
                'time': 0,
                'memory_mb': 0,
                'text_length': 0,
                'chars_per_second': 0,
                'error': str(e)
            }
    
    def test_pdf(self, pdf_path: str, runs: int = 3) -> Dict:
        """Test all available libraries on a single PDF"""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        pdf_name = os.path.basename(pdf_path)
        print(f"\nTesting PDF: {pdf_name}")
        print("=" * 50)
        
        results = {}
        
        # Define extraction methods
        extraction_methods = {
            'pypdf2': (self.extract_with_pypdf2, libraries_available['pypdf2']),
            'pdfplumber': (self.extract_with_pdfplumber, libraries_available['pdfplumber']),
            'pymupdf': (self.extract_with_pymupdf, libraries_available['pymupdf']),
            'pdfminer': (self.extract_with_pdfminer, libraries_available['pdfminer']),
            'markitdown': (self.extract_with_markitdown, libraries_available['markitdown'])
        }
        
        for library_name, (extraction_func, available) in extraction_methods.items():
            if not available:
                print(f"⏭️  Skipping {library_name} (not installed)")
                continue
            
            print(f"🔄 Testing {library_name}...")
            
            # Run multiple times and collect results
            run_results = []
            for run in range(runs):
                result = self.measure_extraction(extraction_func, pdf_path, library_name)
                run_results.append(result)
                
                if result['success']:
                    print(f"   Run {run + 1}: {result['time']:.3f}s, "
                          f"{result['memory_mb']:.2f}MB, "
                          f"{result['text_length']} chars")
                else:
                    print(f"   Run {run + 1}: ❌ Error - {result['error']}")
            
            # Calculate statistics
            successful_runs = [r for r in run_results if r['success']]
            
            if successful_runs:
                times = [r['time'] for r in successful_runs]
                memories = [r['memory_mb'] for r in successful_runs]
                text_lengths = [r['text_length'] for r in successful_runs]
                
                results[library_name] = {
                    'success_rate': len(successful_runs) / runs,
                    'avg_time': statistics.mean(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'std_time': statistics.stdev(times) if len(times) > 1 else 0,
                    'avg_memory_mb': statistics.mean(memories),
                    'avg_text_length': statistics.mean(text_lengths),
                    'avg_chars_per_second': statistics.mean([r['chars_per_second'] for r in successful_runs]),
                    'errors': [r['error'] for r in run_results if not r['success']]
                }
                
                print(f"✅ {library_name}: Avg {results[library_name]['avg_time']:.3f}s, "
                      f"{results[library_name]['avg_memory_mb']:.2f}MB")
            else:
                results[library_name] = {
                    'success_rate': 0,
                    'errors': [r['error'] for r in run_results]
                }
                print(f"❌ {library_name}: All runs failed")
        
        return results
    
    def print_comparison(self, results: Dict, pdf_name: str):
        """Print a formatted comparison of results"""
        print(f"\n📊 PERFORMANCE COMPARISON - {pdf_name}")
        print("=" * 80)
        
        # Filter successful results
        successful = {k: v for k, v in results.items() if v.get('success_rate', 0) > 0}
        
        if not successful:
            print("❌ No libraries successfully extracted text from this PDF")
            return
        
        # Sort by average time
        sorted_results = sorted(successful.items(), key=lambda x: x[1]['avg_time'])
        
        print(f"{'Library':<12} {'Time (s)':<10} {'Memory (MB)':<12} {'Chars':<10} {'Chars/s':<12} {'Success':<8}")
        print("-" * 80)
        
        for library, data in sorted_results:
            print(f"{library:<12} "
                  f"{data['avg_time']:<10.3f} "
                  f"{data['avg_memory_mb']:<12.2f} "
                  f"{data['avg_text_length']:<10.0f} "
                  f"{data['avg_chars_per_second']:<12.0f} "
                  f"{data['success_rate']:<8.1%}")
        
        # Show fastest and most efficient
        if len(sorted_results) > 1:
            fastest = sorted_results[0]
            most_efficient = min(successful.items(), key=lambda x: x[1]['avg_memory_mb'])
            
            print(f"\n🏆 Fastest: {fastest[0]} ({fastest[1]['avg_time']:.3f}s)")
            print(f"💾 Most Memory Efficient: {most_efficient[0]} ({most_efficient[1]['avg_memory_mb']:.2f}MB)")
        
        # Show any errors
        failed = {k: v for k, v in results.items() if v.get('success_rate', 0) == 0}
        if failed:
            print(f"\n❌ Failed Libraries:")
            for library, data in failed.items():
                print(f"   {library}: {data['errors'][0] if data['errors'] else 'Unknown error'}")
    
    def test_multiple_pdfs(self, pdf_paths: List[str], runs: int = 3):
        """Test multiple PDFs and show overall comparison"""
        all_results = {}
        
        for pdf_path in pdf_paths:
            pdf_name = os.path.basename(pdf_path)
            results = self.test_pdf(pdf_path, runs)
            all_results[pdf_name] = results
            self.print_comparison(results, pdf_name)
        
        # Overall summary if multiple PDFs
        if len(pdf_paths) > 1:
            self.print_overall_summary(all_results)
    
    def print_overall_summary(self, all_results: Dict):
        """Print overall summary across all PDFs"""
        print(f"\n🎯 OVERALL SUMMARY ACROSS ALL PDFs")
        print("=" * 80)
        
        # Collect all library results
        library_stats = {}
        
        for pdf_name, results in all_results.items():
            for library, data in results.items():
                if data.get('success_rate', 0) > 0:
                    if library not in library_stats:
                        library_stats[library] = []
                    library_stats[library].append(data)
        
        if not library_stats:
            print("❌ No successful extractions across all PDFs")
            return
        
        print(f"{'Library':<12} {'Avg Time (s)':<12} {'Avg Memory (MB)':<15} {'Success Rate':<12}")
        print("-" * 80)
        
        for library, stats_list in library_stats.items():
            avg_time = statistics.mean([s['avg_time'] for s in stats_list])
            avg_memory = statistics.mean([s['avg_memory_mb'] for s in stats_list])
            avg_success = statistics.mean([s['success_rate'] for s in stats_list])
            
            print(f"{library:<12} "
                  f"{avg_time:<12.3f} "
                  f"{avg_memory:<15.2f} "
                  f"{avg_success:<12.1%}")


def main():
    """Main function with example usage"""
    tester = PDFExtractionTester()
    
    # Check if any libraries are available
    available_count = sum(libraries_available.values())
    if available_count == 0:
        print("❌ No PDF extraction libraries are installed!")
        print("\nTo install all libraries, run:")
        print("pip install PyPDF2 pdfplumber PyMuPDF pdfminer.six markitdown")
        return
    
    print(f"📚 PDF Text Extraction Performance Tester")
    print(f"Available libraries: {available_count}/5")
    print("-" * 50)
    
    # Example usage - you'll need to provide actual PDF paths
    pdf_paths = [
        "TTE P&S_Quotation Design_Dubai.pdf",  # Replace with actual PDF paths
    ]
    
    # Filter to existing files
    existing_pdfs = [path for path in pdf_paths if os.path.exists(path)]
    
    if not existing_pdfs:
        print("❌ No PDF files found. Please update the pdf_paths list with actual PDF file paths.")
        print("\nExample usage:")
        print('tester.test_multiple_pdfs(["your_file.pdf"], runs=3)')
        return
    
    print(f"Testing {len(existing_pdfs)} PDF file(s)...")
    
    # Run the tests
    tester.test_multiple_pdfs(existing_pdfs, runs=3)


if __name__ == "__main__":
    main()
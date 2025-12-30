
import logging
import io
import os
import time
from docx import Document
import pymupdf4llm # Uses PyMuPDF, optimized for LLM-friendly Markdown output
import pymupdf # Required for creating document objects
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from azure.ai.formrecognizer import DocumentAnalysisClient

# Define custom exceptions for clear error handling
class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
    pass

class DocumentProcessingError(Exception):
    """Custom exception for general document processing errors."""
    pass

def extract_with_azure_doc_intelligence(file_bytes: bytes) -> str:
    """
    Extracts text/layout from a file (PDF or Image) using Azure Document Intelligence.
    Implements a fallback mechanism:
    1. Try Primary (F0) credentials.
    2. If Quota Exceeded (429/403), try Secondary (S0) credentials.
    """
    
    # helper to perform the actual extraction call
    def call_doc_intelligence(endpoint, key, content):
        credential = AzureKeyCredential(key)
        client = DocumentAnalysisClient(endpoint=endpoint, credential=credential)
        
        poller = client.begin_analyze_document(
            model_id="prebuilt-layout", 
            document=content
        )
        result = poller.result()
        return result.content

    # Load credentials
    endpoint_primary = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key_primary = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    endpoint_secondary = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT_SECONDARY")
    key_secondary = os.environ.get("AZURE_DOCUMENT_INTELLIGENCE_KEY_SECONDARY")

    if not endpoint_primary or not key_primary:
        raise DocumentProcessingError("Primary Azure Document Intelligence credentials are not configured.")

    try:
        # ATTEMPT 1: Primary (F0)
        logging.info("Attempting OCR with Primary (F0) credentials.")
        return call_doc_intelligence(endpoint_primary, key_primary, file_bytes)

    except HttpResponseError as e:
        status_code = e.status_code if hasattr(e, 'status_code') else 0
        error_msg = str(e).lower()
        
        # Check for Quota/Throttling errors
        # 429: Too Many Requests
        # 403: Out of Call Volume Quota (common for F0)
        is_quota_error = status_code == 429 or status_code == 403 or "quota" in error_msg
        
        if is_quota_error and endpoint_secondary and key_secondary:
            logging.warning(f"Primary OCR tier quota exceeded (Status: {status_code}). Failing over to Secondary (S0) tier.")
            try:
                # ATTEMPT 2: Secondary (S0)
                return call_doc_intelligence(endpoint_secondary, key_secondary, file_bytes)
            except Exception as secondary_error:
                logging.error(f"Secondary OCR tier also failed: {secondary_error}")
                raise DocumentProcessingError(f"OCR failed on both tiers. Primary: {e}. Secondary: {secondary_error}")
        else:
            # Not a quota error or no secondary credentials
            logging.error(f"Azure Document Intelligence error: {e}")
            raise DocumentProcessingError(f"Azure Document Intelligence error: {e}")

    except Exception as e:
        logging.error(f"Unexpected error during OCR: {e}")
        raise DocumentProcessingError(f"Unexpected error during OCR: {e}")

def extract_markdown_from_file(file_name: str, file_bytes: bytes) -> str:
    """
    Extracts text from PDF or DOCX files and converts it to Markdown.
    
    Args:
        file_name (str): The name of the file, used to determine the file type.
        file_bytes (bytes): The raw byte content of the file.

    Returns:
        str: The extracted text in Markdown format.

    Raises:
        UnsupportedFileType: If the file extension is not supported.
        DocumentProcessingError: If the document is corrupt or text extraction fails.
    """
    # Input validation
    if not file_name or not isinstance(file_name, str):
        raise DocumentProcessingError("Invalid file name provided")
    
    if not file_bytes or not isinstance(file_bytes, bytes):
        raise DocumentProcessingError("Invalid file content provided")
    
    if len(file_bytes) == 0:
        raise DocumentProcessingError(f"File {file_name} is empty")
    
    logging.info(f"Starting text extraction for file: {file_name} ({len(file_bytes)} bytes)")
    
    # Extract file extension
    file_parts = file_name.lower().split('.')
    if len(file_parts) < 2:
        raise UnsupportedFileType(f"File {file_name} has no extension.")
    
    file_extension = file_parts[-1]
    supported_extensions = ['pdf', 'docx', 'jpg', 'jpeg', 'png', 'bmp', 'tiff']
    
    if file_extension not in supported_extensions:
        raise UnsupportedFileType(f"Unsupported file type: '{file_extension}'. Supported: {', '.join(supported_extensions)}")

    try:
        markdown_text = ""
        
        # Strategy:
        # 1. Image files -> Direct to Azure OCR
        # 2. PDF files -> Try PyMuPDF first (fast, free). If text is sparse (scanned), fallback to Azure OCR.
        # 3. DOCX files -> Standard extraction
        
        if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
            logging.info(f"Image file detected ({file_extension}). Using Azure Document Intelligence.")
            return extract_with_azure_doc_intelligence(file_bytes)
            
        elif file_extension == 'pdf':
            # Try standard extraction first
            try:
                pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
                
                if pdf_doc.page_count == 0:
                    raise DocumentProcessingError(f"PDF {file_name} appears to be empty (0 pages)")
                
                # Hybrid Approach: Page-by-Page Validation
                # We extract markdown per page and validate against raw text to ensure no content (like headers) is lost.
                
                # Get markdown chunks for each page
                md_chunks = pymupdf4llm.to_markdown(pdf_doc, page_chunks=True)
                
                final_markdown_parts = []
                
                # Iterate through pages to validate each one
                for i, page_md in enumerate(md_chunks):
                    # Get the corresponding raw text for this page
                    if i < len(pdf_doc):
                        raw_text = pdf_doc[i].get_text()
                        
                        # Normalize texts for comparison (remove whitespace)
                        # We check if the first significant chunk of raw text exists in the markdown
                        clean_raw = "".join(raw_text.split())[:100]
                        clean_md = "".join(page_md['text'].split())
                        
                        if clean_raw and clean_raw not in clean_md:
                            logging.warning(f"Potential content stripping detected on page {i+1} of {file_name}. Prepending raw text.")
                            # Prepend raw text to this page's markdown
                            final_markdown_parts.append(f"{raw_text}\n\n---\n\n{page_md['text']}")
                        else:
                            final_markdown_parts.append(page_md['text'])
                    else:
                        final_markdown_parts.append(page_md['text'])
                
                markdown_text = "\n\n".join(final_markdown_parts)
                
                # Heuristic check for scanned PDF:
                # If extracted text is very short relative to page count, it's likely scanned.
                # Threshold: < 50 characters per page average
                char_count = len(markdown_text.strip())
                avg_chars_per_page = char_count / pdf_doc.page_count
                
                logging.info(f"PDF Standard Extraction: {char_count} chars, {pdf_doc.page_count} pages. Avg: {avg_chars_per_page:.1f}")
                
                if avg_chars_per_page < 50:
                    logging.warning(f"Low text density detected ({avg_chars_per_page:.1f} chars/page). Likely scanned PDF. Falling back to OCR.")
                    markdown_text = extract_with_azure_doc_intelligence(file_bytes)
                
                pdf_doc.close()
                
            except Exception as e:
                logging.warning(f"Standard PDF extraction failed: {e}. Attempting fallback to OCR.")
                markdown_text = extract_with_azure_doc_intelligence(file_bytes)

        elif file_extension == 'docx':
            # For DOCX, we can build a simple Markdown representation.
            try:
                document = Document(io.BytesIO(file_bytes))
                markdown_parts = []
                for para in document.paragraphs:
                    if para.text.strip():
                        if para.runs and any(run.bold for run in para.runs):
                            markdown_parts.append(f"## {para.text.strip()}\n")
                        else:
                            markdown_parts.append(f"{para.text.strip()}\n")
                markdown_text = "\n".join(markdown_parts)
            except Exception as docx_error:
                raise DocumentProcessingError(f"Failed to process DOCX file {file_name}: {docx_error}")

        if not markdown_text or not markdown_text.strip():
            raise DocumentProcessingError(f"No text could be extracted from {file_name}. The file may be empty or image-based.")

        logging.info(f"Successfully extracted {len(markdown_text)} characters from {file_name}.")
        return markdown_text

    except UnsupportedFileType:
        raise
    except Exception as e:
        logging.error(f"Failed to process document {file_name}. Error: {e}")
        raise DocumentProcessingError(f"A library error occurred while processing {file_name}: {e}")
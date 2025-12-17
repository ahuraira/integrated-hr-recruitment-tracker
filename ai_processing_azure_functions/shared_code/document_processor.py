# /shared_code/document_processor.py

import logging
import io
from docx import Document
# /shared_code/document_processor.py

import logging
import io
import os
from docx import Document
import pymupdf4llm # Uses PyMuPDF, optimized for LLM-friendly Markdown output
import pymupdf # Required for creating document objects
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Define custom exceptions for clear error handling
class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
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
                
                # Extract text using PyMuPDF4LLM
                markdown_text = pymupdf4llm.to_markdown(pdf_doc)
                
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
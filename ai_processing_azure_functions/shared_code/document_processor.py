# /shared_code/document_processor.py

import logging
import io
from docx import Document
import pymupdf4llm # Uses PyMuPDF, optimized for LLM-friendly Markdown output
import pymupdf # Required for creating document objects

# Define custom exceptions for clear error handling
class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
# /shared_code/document_processor.py

import logging
import io
from docx import Document
import pymupdf4llm # Uses PyMuPDF, optimized for LLM-friendly Markdown output
import pymupdf # Required for creating document objects

# Define custom exceptions for clear error handling
class UnsupportedFileType(Exception):
    """Custom exception for unsupported file types."""
    pass

class DocumentProcessingError(Exception):
    """Custom exception for errors during document parsing."""
    pass

def extract_markdown_from_file(file_name: str, file_bytes: bytes) -> str:
    """
    Extracts structured Markdown text from a given file (PDF or DOCX).

    Args:
        file_name (str): The name of the file, used to determine the file type.
        file_bytes (bytes): The raw byte content of the file.

    Returns:
        str: The extracted text in Markdown format.

    Raises:
        UnsupportedFileType: If the file extension is not .pdf or .docx.
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
        raise UnsupportedFileType(f"File {file_name} has no extension. Only .pdf and .docx are supported.")
    
    file_extension = file_parts[-1]

    try:
        markdown_text = ""
        if file_extension == 'pdf':
            # PyMuPDF4LLM is highly efficient and designed for this exact use case
            # It uses PyMuPDF under the hood but with better formatting for AI
            pdf_doc = None
            try:
                # Create a PyMuPDF document object from bytes
                pdf_doc = pymupdf.open(stream=file_bytes, filetype="pdf")
                
                # Validate the PDF was opened successfully
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
                
            except pymupdf.FileDataError as pdf_error:
                raise DocumentProcessingError(f"Invalid or corrupted PDF file {file_name}: {pdf_error}")
            except Exception as pdf_error:
                raise DocumentProcessingError(f"Failed to process PDF file {file_name}: {pdf_error}")
            finally:
                # Always close the document to free memory
                if pdf_doc is not None:
                    try:
                        pdf_doc.close()
                    except:
                        pass  # Ignore close errors

        elif file_extension == 'docx':
            # For DOCX, we can build a simple Markdown representation.
            try:
                document = Document(io.BytesIO(file_bytes))
                markdown_parts = []
                for para in document.paragraphs:
                    if para.text.strip():  # Only add non-empty paragraphs
                        # Basic heuristic: Treat paragraphs with bold runs as headings
                        if para.runs and any(run.bold for run in para.runs):
                            markdown_parts.append(f"## {para.text.strip()}\n")
                        else:
                            markdown_parts.append(f"{para.text.strip()}\n")
                markdown_text = "\n".join(markdown_parts)
            except Exception as docx_error:
                raise DocumentProcessingError(f"Failed to process DOCX file {file_name}: {docx_error}")
            
        else:
            raise UnsupportedFileType(f"Unsupported file type: '{file_extension}'. Only .pdf and .docx are supported.")

        if not markdown_text or not markdown_text.strip():
            raise DocumentProcessingError(f"No text could be extracted from {file_name}. The file may be empty or image-based.")

        logging.info(f"Successfully extracted {len(markdown_text)} characters from {file_name}.")
        return markdown_text

    except UnsupportedFileType:
        # Re-raise the specific exception to be caught by the main function
        raise
    except Exception as e:
        # Catch any other generic library errors (e.g., corrupt file)
        logging.error(f"Failed to process document {file_name}. Error: {e}")
        raise DocumentProcessingError(f"A library error occurred while processing {file_name}: {e}")
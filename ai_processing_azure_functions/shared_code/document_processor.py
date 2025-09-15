# /shared_code/document_processor.py

import logging
import io
from docx import Document
import pymupdf4llm # Uses PyMuPDF, optimized for LLM-friendly Markdown output

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
    logging.info(f"Starting text extraction for file: {file_name}")
    
    file_extension = file_name.lower().split('.')[-1]

    try:
        markdown_text = ""
        if file_extension == 'pdf':
            # PyMuPDF4LLM is highly efficient and designed for this exact use case
            # It uses PyMuPDF under the hood but with better formatting for AI
            markdown_text = pymupdf4llm.to_markdown(file_bytes)

        elif file_extension == 'docx':
            # For DOCX, we can build a simple Markdown representation.
            # A more advanced library could be used here if needed, but this is robust.
            document = Document(io.BytesIO(file_bytes))
            markdown_parts = []
            for para in document.paragraphs:
                # Basic heuristic: Treat paragraphs with bold runs as headings
                if para.runs and any(run.bold for run in para.runs):
                    markdown_parts.append(f"## {para.text}\n")
                else:
                    markdown_parts.append(f"{para.text}\n")
            markdown_text = "\n".join(markdown_parts)
            
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
from flask import Request
from langchain_core.tools import tool
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredWordDocumentLoader,
)
import os

from src.flask.supabase.transcript import insert_transcript


@tool(parse_docstring=True)
def extract_text_from_docx_file(file_path: str) -> str:
    """Extract and return raw text content from a Word Document.

    Args:
        file_path: The path to the docx file.
    """
    try:
        print(f"Extracting text from file: {file_path}")
        if not os.path.exists(file_path):
            return f"Error: File does not exist at path: {file_path}"

        if not os.path.isfile(file_path):
            return f"Error: Path exists but is not a file: {file_path}"

        loader = UnstructuredWordDocumentLoader(file_path)
        documents = loader.load()

        if not documents:
            return f"Error: No content found in file: {file_path}"

        content = "\n".join([doc.page_content for doc in documents])

        if not content.strip():
            return f"Error: File appears to be empty: {file_path}"

        return content

    except Exception as e:
        return f"Error reading file '{file_path}': {type(e).__name__}: {str(e)}"


@tool(parse_docstring=True)
def extract_text_from_file(file_path: str) -> str:
    """Extract and return raw text content from a file.

    Args:
        file_path: The path to the file to extract text from.
    """

    try:
        # Debug information
        if not os.path.exists(file_path):
            return f"Error: File does not exist at path: {file_path}"

        if not os.path.isfile(file_path):
            return f"Error: Path exists but is not a file: {file_path}"

        # Try to read the file
        loader = TextLoader(file_path)
        documents = loader.load()

        if not documents:
            return f"Error: No content found in file: {file_path}"

        content = "\n".join([doc.page_content for doc in documents])

        if not content.strip():
            return f"Error: File appears to be empty: {file_path}"

        return content

    except Exception as e:
        return f"Error reading file '{file_path}': {type(e).__name__}: {str(e)}"


@tool(parse_docstring=True)
def insert_transcript_into_db(text: str, auth_token: str) -> str:
    """Insert the transcript into the database.

    Args:
        text: The transcript to insert.
        auth_token: The auth token.

    Returns:
        The id of the inserted transcript.
    """
    print("Inserting transcript into db with token:", auth_token)
    result = insert_transcript(auth_token, text)

    print("Transcript inserted with id:", result["id"])

    return result["id"]


tools = [
    extract_text_from_docx_file,
    extract_text_from_file,
    insert_transcript_into_db,
]

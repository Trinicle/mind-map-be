from langchain_core.tools import tool
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredWordDocumentLoader,
)
from src.flask.supabase.transcript import insert_transcript


@tool(parse_docstring=True)
def docx_file_to_text(file_path: str) -> str:
    """Extract text from a Word document.

    Args:
        file_path: The path to the docx file.
    """
    loader = UnstructuredWordDocumentLoader(file_path)
    documents = loader.load()
    return "\n".join([doc.page_content for doc in documents])


@tool(parse_docstring=True)
def default_file_to_text(file_path: str) -> str:
    """Extract text from a non-specific file.

    Args:
        file_path: The path to the file.
    """
    loader = TextLoader(file_path)
    documents = loader.load()
    return "\n".join([doc.page_content for doc in documents])


@tool(parse_docstring=True)
def insert_transcript_into_database(transcript: str) -> str | None:
    """Insert a transcript into the database.

    Args:
        transcript: The transcript to insert.
    """
    result = insert_transcript(transcript)
    return result["id"] if result else None


tools = [docx_file_to_text, default_file_to_text, insert_transcript_into_database]

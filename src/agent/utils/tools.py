from langchain_core.tools import tool
from langchain_community.document_loaders import (
    TextLoader,
    UnstructuredWordDocumentLoader,
)


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


tools = [docx_file_to_text]

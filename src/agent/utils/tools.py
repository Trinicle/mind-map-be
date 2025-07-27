from langchain_core.tools import tool
from langchain_community.document_loaders import UnstructuredWordDocumentLoader


@tool(parse_docstring=True)
def docx_file_to_text(file_path: str) -> str:
    """Extract text from a Word document.

    Args:
        file_path: The path to the docx file.
    """
    loader = UnstructuredWordDocumentLoader(file_path)
    documents = loader.load()

    full_text = []
    for doc in documents:
        if doc.page_content.strip():
            full_text.append(doc.page_content)

    return "\n".join(full_text)


tools = [docx_file_to_text]

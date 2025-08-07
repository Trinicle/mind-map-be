import os
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.runnables import ensure_config
from dotenv import load_dotenv


load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-5-mini", temperature=1)
vectorstore = PGVector(
    connection=os.getenv("DATABASE_URL"),
    embeddings=embeddings,
    collection_name="Transcript_Vector",
    use_jsonb=True,
)


@tool(parse_docstring=True)
def query_internet(query: str):
    """Search the internet for the query.

    Args:
        query: The query to search the internet for.

    Returns:
        str: The results of the search.
    """
    search = TavilySearch(
        max_results=2,
        topic="general",
    )
    return search.run(query)


@tool(parse_docstring=True)
def query_transcripts(query: str) -> List[Document]:
    """Query transcripts for the query. Automatically uses transcript context if available, otherwise searches all user transcripts.

    Args:
        query: The query to search the transcript for.

    Returns:
        List[Document]: The results of the search.
    """
    try:
        config = ensure_config()
        metadata = config.get("metadata", {})
        user_id = metadata.get("user_id")
        transcript_id = metadata.get("transcript_id")

        if not user_id:
            raise ValueError("user_id not found in config metadata")

        if transcript_id:
            print(f"Searching within specific transcript: {transcript_id}")
            search = vectorstore.similarity_search(
                query, k=5, filter={"user_id": user_id, "transcript_id": transcript_id}
            )
        else:
            print("Searching across all user transcripts")
            search = vectorstore.similarity_search(
                query, k=5, filter={"user_id": user_id}
            )

        print(search)
        return search
    except Exception as e:
        print(f"Error in query_transcripts: {e}")
        # Fallback: return empty results if config issues
        return []


tools = [query_internet, query_transcripts]

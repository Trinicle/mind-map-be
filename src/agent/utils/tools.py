import os
from typing import List
from langchain_core.embeddings import Embeddings
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv


load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
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
def query_transcript(query: str, user_id: str) -> List[Document]:
    """Query the transcript for the query.

    Args:
        query: The query to search the transcript for.
        user_id: The user id from the user.

    Returns:
        List[Document]: The results of the search.
    """

    return vectorstore.similarity_search(query, k=5, filter={"user_id": user_id})


tools = [query_internet, query_transcript]

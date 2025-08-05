import os
from typing import List
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.vectorstores import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv


load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
vectorstore = PGVector(
    connection_string=os.getenv("DATABASE_URL"),
    embedding=embeddings,
    collection_name="Transcript",
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
    search = TavilySearch()
    return search.run(query)


@tool(parse_docstring=True)
def query_transcript(query: str, user_id: str) -> List[Document]:
    """Query the transcript for the query.

    Args:
        query: The query to search the transcript for.
        auth_token: The auth token from the user.

    Returns:
        str: The results of the search.
    """

    documents = vectorstore.similarity_search(query, k=5, filter={"user_id": user_id})
    pass


tools = [query_internet, query_transcript]

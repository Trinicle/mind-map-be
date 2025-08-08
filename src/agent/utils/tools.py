import os
from typing import List
from contextlib import contextmanager
from langchain_core.embeddings import Embeddings
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from langchain_core.runnables import ensure_config
from dotenv import load_dotenv


load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
title_llm = ChatOpenAI(model="gpt-5-nano", temperature=1, max_completion_tokens=50)


@contextmanager
def get_vectorstore():
    """Create a per-request transcript vectorstore connection with automatic cleanup."""
    vectorstore = None
    try:
        vectorstore = PGVector(
            connection=os.getenv("DATABASE_URL"),
            embeddings=embeddings,
            collection_name="Transcript_Vector",
            use_jsonb=True,
        )
        yield vectorstore
    finally:
        if (
            vectorstore
            and hasattr(vectorstore, "_connection")
            and vectorstore._connection
        ):
            try:
                vectorstore._connection.close()
            except Exception as e:
                print(f"Warning: Error closing vectorstore connection: {e}")


@contextmanager
def get_messages_vectorstore():
    """Create a per-request messages vectorstore connection with automatic cleanup."""
    vectorstore = None
    try:
        vectorstore = PGVector(
            connection=os.getenv("DATABASE_URL"),
            embeddings=embeddings,
            collection_name="Message_Vector",
            use_jsonb=True,
        )
        yield vectorstore
    finally:
        if (
            vectorstore
            and hasattr(vectorstore, "_connection")
            and vectorstore._connection
        ):
            try:
                vectorstore._connection.close()
            except Exception as e:
                print(f"Warning: Error closing messages vectorstore connection: {e}")


def create_title(query: str) -> str:
    messages = [
        SystemMessage(
            content="You are a helpful assistant that creates titles for conversations. For a given query, create a short broad title in under 5 words. If you cannot, default to 'New Conversation'."
        ),
        HumanMessage(content=query),
    ]
    return title_llm.invoke(messages).content


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

        with get_vectorstore() as vectorstore:
            if transcript_id:
                print(f"Searching within specific transcript: {transcript_id}")
                search = vectorstore.similarity_search(
                    query,
                    k=5,
                    filter={"user_id": user_id, "transcript_id": transcript_id},
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


@tool(parse_docstring=True)
def query_messages(query: str) -> List[Document]:
    """Retrieve semantically relevant prior chat messages for additional context
    Uses conversation_id if provided; otherwise falls back to user scope.

    Args:
        query: The query to match against prior messages.

    Returns:
        List[Document]: Relevant message snippets ordered by similarity.
    """
    try:
        config = ensure_config()
        metadata = config.get("metadata", {})
        user_id = metadata.get("user_id")
        conversation_id = metadata.get("conversation_id")

        if not user_id:
            raise ValueError("user_id not found in config metadata")

        filter_dict = {"user_id": user_id}
        if conversation_id:
            filter_dict["conversation_id"] = conversation_id

        with get_messages_vectorstore() as messages_vectorstore:
            search = messages_vectorstore.similarity_search(
                query, k=5, filter=filter_dict
            )
            return search
    except Exception as e:
        print(f"Error in query_messages: {e}")
        return []


tools = [query_internet, query_transcripts, query_messages]

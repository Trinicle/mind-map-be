"""
Database connection pool management for the application.
This module is separate to avoid circular imports.
"""

import os
from redis import Redis
from contextlib import contextmanager
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from langchain_postgres import PGVector
from langchain_redis import RedisChatMessageHistory

load_dotenv()
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")


@contextmanager
def get_vectorstore_context():
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


def get_vectorstore():
    return PGVector(
        connection=os.getenv("DATABASE_URL"),
        embeddings=embeddings,
        collection_name="Transcript_Vector",
        use_jsonb=True,
    )


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


@contextmanager
def get_checkpoint():
    """Create a per-request PostgresSaver instance with automatic cleanup.

    This creates a fresh PostgresSaver for each request to avoid long-running sessions.
    """
    connection_pool = None
    checkpoint = None
    try:
        connection_pool = ConnectionPool(
            conninfo=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=2,
        )
        checkpoint = PostgresSaver(connection_pool)
        yield checkpoint
    finally:
        if connection_pool:
            try:
                connection_pool.close()
            except Exception as e:
                print(f"Warning: Error closing checkpoint connection pool: {e}")


@contextmanager
def get_redis_client():
    """Create a per-request Redis client connection with automatic cleanup."""
    redis_client = None
    try:
        redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
        yield redis_client
    finally:
        if redis_client:
            redis_client.close()


@contextmanager
def get_redis_history_context(conversation_id: str):
    """Create a per-request Redis client connection with automatic cleanup."""
    redis_client = None
    try:
        redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
        redis_history = RedisChatMessageHistory(
            session_id=conversation_id, redis_client=redis_client
        )
        yield redis_history
    finally:
        if redis_client:
            redis_client.close()


def get_redis_history(conversation_id: str):
    redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"))
    return RedisChatMessageHistory(
        session_id=conversation_id, redis_client=redis_client
    )

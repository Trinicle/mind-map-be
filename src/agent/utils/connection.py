"""
Database connection pool management for the application.
This module is separate to avoid circular imports.
"""

import os
from contextlib import contextmanager
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

load_dotenv()


@contextmanager
def get_checkpoint():
    """Create a per-request PostgresSaver instance with automatic cleanup.

    This creates a fresh PostgresSaver for each request to avoid long-running sessions.
    """
    connection_pool = None
    checkpoint = None
    try:
        # Create a new connection pool for this request
        connection_pool = ConnectionPool(
            conninfo=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=2,  # Smaller pool per request
        )
        checkpoint = PostgresSaver(connection_pool)
        yield checkpoint
    finally:
        # Clean up the connection pool for this request
        if connection_pool:
            try:
                connection_pool.close()
            except Exception as e:
                print(f"Warning: Error closing checkpoint connection pool: {e}")

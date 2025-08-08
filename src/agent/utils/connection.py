"""
Database connection pool management for the application.
This module is separate to avoid circular imports.
"""

import os
from dotenv import load_dotenv
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

load_dotenv()

# Global connection pool - shared across the application
_connection_pool = None
_checkpoint_instance = None


def get_connection_pool():
    """Get or create a shared connection pool instance."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = ConnectionPool(
            conninfo=os.getenv("DATABASE_URL"),
            min_size=1,
            max_size=5,  # Limit the pool size to prevent exhausting connections
        )
    return _connection_pool


def get_checkpoint():
    """Get or create a shared checkpoint instance."""
    global _checkpoint_instance
    if _checkpoint_instance is None:
        connection_pool = get_connection_pool()
        _checkpoint_instance = PostgresSaver(connection_pool)
    return _checkpoint_instance


def close_connection_pool():
    """Close the connection pool when shutting down the application."""
    global _connection_pool, _checkpoint_instance
    if _connection_pool:
        _connection_pool.close()
        _connection_pool = None
        _checkpoint_instance = None

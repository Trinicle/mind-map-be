import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool
from src.agent.utils.nodes import (
    contextual_tool_node,
    query_node,
)
from src.agent.utils.state import ChatBotState

load_dotenv()
connection = ConnectionPool(
    conninfo=os.getenv("DATABASE_URL"),
)
checkpoint = PostgresSaver(connection)


def setup_checkpoint():
    try:
        checkpoint.setup()
    except Exception as e:
        print(f"Checkpoint setup failed: {e}")
        pass


chatbot_builder = StateGraph(ChatBotState)

chatbot_builder.add_node("query", query_node)
chatbot_builder.add_node("tools", contextual_tool_node)

chatbot_builder.add_edge(START, "query")
chatbot_builder.add_edge("query", "tools")

chatbot_builder.add_conditional_edges(
    "tools",
    tools_condition,
    {
        "tools": "tools",
        END: END,
    },
)

chatbot = chatbot_builder.compile(checkpointer=checkpoint)

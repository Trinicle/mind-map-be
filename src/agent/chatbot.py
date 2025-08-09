from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from src.agent.connection import get_checkpoint
from src.agent.nodes import (
    contextual_tool_node,
    query_node,
    response_node,
)
from src.agent.state import ChatBotState


def initialize_chatbot(checkpoint):
    """Initialize chatbot with a checkpoint instance.

    Args:
        checkpoint: PostgresSaver instance (required).
    """
    if checkpoint is None:
        raise ValueError("checkpoint parameter is required for initialize_chatbot()")

    chatbot_builder = StateGraph(ChatBotState)

    chatbot_builder.add_node("query", query_node)
    chatbot_builder.add_node("tools", contextual_tool_node)
    chatbot_builder.add_node("response", response_node)

    chatbot_builder.add_edge(START, "query")
    chatbot_builder.add_edge("query", "tools")

    chatbot_builder.add_conditional_edges(
        "tools",
        tools_condition,
        {
            "tools": "tools",
            END: "response",
        },
    )

    chatbot_builder.add_edge("response", END)

    return chatbot_builder.compile(checkpointer=checkpoint)

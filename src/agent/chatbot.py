from typing import Optional
import uuid
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_postgres import PGVector
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt.tool_node import ToolNode
from src.agent.connection import get_redis_history
from langchain_core.messages import BaseMessage
from src.agent.prompts import ChatBotPrompts
from src.agent.state import ChatBotState
from langchain_core.tools.retriever import create_retriever_tool

from src.agent.tools import tools


class FilteredChatMessageHistory(BaseChatMessageHistory):
    """Wrapper around Redis history that filters out tool messages for clean conversation flow."""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self._redis_history = get_redis_history(session_id)

    @property
    def messages(self) -> list[BaseMessage]:
        """Return messages filtered to exclude tool messages."""
        all_messages = self._redis_history.messages
        filtered_messages = [
            msg
            for msg in all_messages
            if not (
                hasattr(msg, "additional_kwargs")
                and msg.additional_kwargs.get("tool_calls") is not None
            )
        ]
        return filtered_messages

    def add_message(self, message: BaseMessage) -> None:
        """Add message to Redis history."""
        id = message.id
        if id is None:
            id = str(uuid.uuid4())
        message.additional_kwargs["id"] = id
        print(message)
        self._redis_history.add_message(message)

    def clear(self) -> None:
        """Clear Redis history."""
        self._redis_history.clear()


def get_filtered_redis_history(session_id: str) -> FilteredChatMessageHistory:
    """Get filtered Redis history that excludes tool messages."""
    return FilteredChatMessageHistory(session_id)


def create_rag_agent(
    checkpoint,
    llm: ChatOpenAI,
    vectorstore: PGVector,
    user_id: str,
    conversation_id: str,
    transcript_id: Optional[str] = None,
):
    config = {
        "configurable": {
            "session_id": conversation_id,
        },
        "metadata": {
            "user_id": user_id,
            "transcript_id": transcript_id,
            "conversation_id": conversation_id,
        },
    }

    filters = {
        "user_id": user_id,
    }
    if transcript_id:
        filters["transcript_id"] = transcript_id

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ChatBotPrompts.CHATBOT_SYSTEM),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3,
            "filter": filters,
        }
    )
    retriever_tool = create_retriever_tool(
        retriever,
        name="transcript_retriever",
        description="A tool that can retrieve information from the transcript or meeting",
    )
    all_tools = [retriever_tool] + tools

    llm_with_tools = llm.bind_tools(all_tools)

    chain = prompt | llm_with_tools

    llm_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history=get_filtered_redis_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    def chatbot(state: ChatBotState):
        query = state.messages[-1].content
        return {"messages": [llm_with_history.invoke({"input": query}, config=config)]}

    def response_node(state: ChatBotState):
        dynamic_message = state.messages[-2]

        if dynamic_message.type == "human":
            return {"messages": []}

        synthesis_prompt = SystemMessage(
            content="""You are a helpful assistant. Based on the tool results and conversation history, 
        provide a clear, helpful response to the user. Synthesize the information from the tools 
        into a natural, conversational response."""
        )

        context_messages = [synthesis_prompt] + state.messages

        ai_response = llm.invoke(context_messages, config=config)

        session_id = config["configurable"]["session_id"]
        history = get_filtered_redis_history(session_id)
        history.add_message(ai_response)

        return {"messages": [ai_response]}

    tools_node = ToolNode(tools=all_tools)

    rag_graph = StateGraph(ChatBotState)

    rag_graph.add_node("query", chatbot)
    rag_graph.add_node("tools", tools_node)
    rag_graph.add_node("response", response_node)

    rag_graph.add_edge(START, "query")

    rag_graph.add_conditional_edges(
        "query",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "response",
        },
    )

    rag_graph.add_conditional_edges(
        "tools",
        tools_condition,
        {
            "tools": "tools",
            "__end__": "response",
        },
    )

    rag_graph.add_edge("response", END)

    return rag_graph.compile(checkpointer=checkpoint)

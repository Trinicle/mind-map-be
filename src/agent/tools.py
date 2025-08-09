from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv


load_dotenv()
title_llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=1, max_completion_tokens=50)


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
    """Search the internet to answer the query.

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


tools = [query_internet]

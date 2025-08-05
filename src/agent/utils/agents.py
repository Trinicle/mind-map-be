from langchain.agents import create_react_agent
from langchain_openai import ChatOpenAI

from src.agent.utils.tools import tools

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)

agent = create_react_agent(llm, tools)

from datetime import datetime
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage

from src.agent.utils.prompts import get_transcript_prompt
from src.agent.utils.tools import tools
from src.flask.models.mindmap_models import MindMapAgentOutput
from src.flask.models.topic_models import Topic


# agent_prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are an AI assistant that analyzes meeting transcripts to extract meaningful topics and insights.",
#         ),
#         ("human", "{instructions}"),
#         MessagesPlaceholder(variable_name="agent_scratchpad"),
#     ]
# )

# # Create the agent with tools and prompt
# agent = create_openai_functions_agent(llm, tools, agent_prompt)
# agent_executor = AgentExecutor(agent=agent, tools=tools, handle_parsing_errors=True)


# def analyze_transcript(
#     title: str,
#     description: str,
#     date: datetime,
#     file_path: str,
#     auth_token: str,
# ) -> dict | None:
#     """Analyze transcript content and return structured data for mindmap creation.

#     Returns a dictionary with cleaned_transcript, participants, topics, and connections.
#     """
#     prompt = get_transcript_prompt(file_path, title, description, date, auth_token)
#     response = agent_executor.invoke({"instructions": prompt})

#     output_data = response["output"]
#     print(output_data)
#     if isinstance(output_data, str):
#         try:
#             return json.loads(output_data)
#         except json.JSONDecodeError:
#             return None

#     return output_data if isinstance(output_data, dict) else None


# def create_topic_suggestive_questions(topic: Topic):
#     pass

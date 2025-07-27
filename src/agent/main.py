from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from src.agent.utils.tools import tools
from src.agent.utils.prompts import get_transcript_prompt
from src.models import MindMap

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

agent_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful AI assistant that can analyze documents and create structured summaries.",
        ),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# Create the agent with tools and prompt
agent = create_openai_tools_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


def create_mindmap(mindmap: MindMap):
    prompt = get_transcript_prompt(mindmap["file_path"])
    response = agent_executor.invoke({"input": prompt})
    print(response["output"])


if __name__ == "__main__":
    mindmap: MindMap = {
        "title": "Test Mindmap",
        "description": "Test Description",
        "date": datetime.now(),
        "tags": ["test", "mindmap"],
        "file_path": "uploads/test_file.docx",
    }
    create_mindmap(mindmap)

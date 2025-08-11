import asyncio
from flask import Request
from langchain_openai import ChatOpenAI
from src.agent.state import ContentState, TopicState
from src.flask.models.content_models import BasicContent
from src.flask.models.topic_models import Topic, TopicDetail
from src.flask.supabase.client import get_client, get_async_client
from src.flask.supabase.content import insert_content_async

llm = ChatOpenAI(model="gpt-5-nano", temperature=1)


def get_topics(request: Request, mindmap_id: str) -> list[Topic]:
    """
    Get all topics for the current user.
    """
    client = get_client(request)
    result = client.table("Topic").select("*").eq("mindmap_id", mindmap_id).execute()
    data = result.data if result.data else []
    return [
        Topic(
            id=topic["id"],
            title=topic["title"],
            mindmap_id=topic["mindmap_id"],
            user_id=topic["user_id"],
            updated_at=topic["updated_at"],
            created_at=topic["created_at"],
            connected_topics=topic["connected_topics"],
        )
        for topic in data
    ]


def get_topic_detail(request: Request, topic_id: str) -> TopicDetail:
    client = get_client(request)
    topic_result = client.table("Topic").select("*").eq("id", topic_id).execute()
    contents_result = (
        client.table("Content").select("*").eq("topic_id", topic_id).execute()
    )

    topic_data = topic_result.data[0]
    contents_data = contents_result.data
    print(contents_data)

    topic_detail = TopicDetail(
        id=topic_data["id"],
        title=topic_data["title"],
        content=[
            BasicContent(
                id=content["id"],
                speaker=content["speaker"],
                text=content["text"],
            )
            for content in contents_data
        ],
    )
    return topic_detail


def insert_topic(
    request: Request, title: str, connected_topics: list[str], mindmap_id: str
) -> Topic | None:
    """
    Insert a new topic for the current user.
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
        "connected_topics": connected_topics,
    }

    client = get_client(request)
    result = client.table("Topic").insert(data).execute()
    data = result.data[0] if result.data else None
    return Topic(
        id=data["id"],
        title=data["title"],
        mindmap_id=data["mindmap_id"],
        user_id=data["user_id"],
        updated_at=data["updated_at"],
        created_at=data["created_at"],
        connected_topics=data["connected_topics"],
    )


async def insert_topic_async(
    request: Request, title: str, connected_topics: list[str], mindmap_id: str
) -> Topic | None:
    """
    Insert a new topic for the current user (async version).
    """
    data = {
        "title": title,
        "mindmap_id": mindmap_id,
        "connected_topics": connected_topics,
    }

    client = await get_async_client(request)
    result = await client.table("Topic").insert(data).execute()
    data = result.data[0] if result.data else None
    return Topic(
        id=data["id"],
        title=data["title"],
        mindmap_id=data["mindmap_id"],
        user_id=data["user_id"],
        updated_at=data["updated_at"],
        created_at=data["created_at"],
        connected_topics=data["connected_topics"],
    )


async def insert_topic_with_content_async(
    request: Request,
    topic_data: TopicState,
    connected_topics: list[str],
    mindmap_id: str,
    contents: list[ContentState],
):
    tasks = []
    topic = await insert_topic_async(
        request, topic_data.title, connected_topics, mindmap_id
    )

    for content in contents:
        task = insert_content_async(request, content.text, content.speaker, topic.id)
        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)

    return topic

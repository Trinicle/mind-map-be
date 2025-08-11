import asyncio
from typing import List
from flask import Request
from src.flask.models.question_models import Question
from src.flask.supabase.client import get_async_client, get_client


async def insert_questions_async(
    request: Request, questions: List[str], mindmap_id: str
):
    client = await get_async_client(request)
    tasks = []
    for question in questions:
        data = {
            "question": question,
            "mindmap_id": mindmap_id,
        }
        tasks.append(client.table("Question").insert(data).execute())
    await asyncio.gather(*tasks)


def get_questions(request: Request, mindmap_id: str) -> List[Question]:
    client = get_client(request)
    result = client.table("Question").select("*").eq("mindmap_id", mindmap_id).execute()
    data = result.data
    questions = [Question(**question) for question in data]
    return questions

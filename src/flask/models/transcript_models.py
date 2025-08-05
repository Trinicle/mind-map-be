from pydantic import BaseModel


class Transcript(BaseModel):
    id: str
    user_id: str
    text: str

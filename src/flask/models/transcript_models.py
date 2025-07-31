from datetime import datetime
from gotrue import TypedDict


class Transcript(TypedDict):
    id: str
    user_id: str
    text: str
    created_at: datetime
    updated_at: datetime

from datetime import datetime
from gotrue import TypedDict


class Transcript(TypedDict):
    id: str
    user_id: str
    text: str

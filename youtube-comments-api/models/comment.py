from dataclasses import dataclass
from typing import List

@dataclass
class Comment:
    text: str
    user_name: str
    date: str
    replies: List[str]
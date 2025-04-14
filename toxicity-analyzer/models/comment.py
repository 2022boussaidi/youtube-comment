from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class CommentAnalysis:
    original_comment: str
    cleaned_comment: str
    toxicity_score: Dict[str, Any]
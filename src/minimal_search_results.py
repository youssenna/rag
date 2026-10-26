from pydantic import BaseModel
from .minimal_source import MinimalSource
from typing import List


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: List[MinimalSource]
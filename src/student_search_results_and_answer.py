from pydantic import BaseModel
from .minimal_answer import MinimalAnswer
from typing import List


class StudentSearchResultsAndAnswer(BaseModel):
    search_results: List[MinimalAnswer]
    k: int

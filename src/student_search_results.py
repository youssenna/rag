from pydantic import BaseModel
from .minimal_search_results import MinimalSearchResults
from typing import List


class StudentSearchResults(BaseModel):
    search_results: List[MinimalSearchResults]
    k: int
    
    

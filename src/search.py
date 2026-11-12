import bm25s
import json
from .utils import Chunk, MinimalSource
from typing import List

class Search:
    def __init__(self, query: str, k: int):
        self.query: str = query
        self.k: int = k
        
        
    def run(self, debug: bool):
        retrive = bm25s.BM25.load('data/processed/index')
        query_tokens = bm25s.tokenize(self.query)
        docs, scores = retrive.retrieve(query_tokens, k=self.k, leave_progress=True)
        with open('data/processed/chunks.json', 'r', encoding='utf-8') as f:
            data: List[Chunk] = json.load(f)
        # print(data)
        results: List[MinimalSource] = []
        for index, score in zip(docs.tolist()[0], scores.tolist()[0]):
            if score:
                source = MinimalSource(file_path=data[index]['file_path'],
                                       first_character_index=data[index]['first_character_index'],
                                       last_character_index=data[index]['last_character_index']
                                       )
                results.append(source)        
                if debug:
                    print("="*30)
                    print(f'score = {score}:', source.file_path,
                          f"[{source.first_character_index}: {source.last_character_index}]")
import fire
import tqdm
import ast
import pathlib
from .pipline import Pipline
from typing import List
from .index import PyFileChunker
import bm25s




def main():
    corpus = ["helo world From morroco_",
              'yes i am 1337 STUDENT',
              'test morroco_ test allah',
              'welcome to the fUtuer']
    corpus_tokens = bm25s.tokenize(corpus)
    print(corpus_tokens)
    retriver = bm25s.BM25(corpus=corpus)
    retriver.index(corpus_tokens)
    
    query = "are you from morroco_"
    query_tokens = bm25s.tokenize(query)
    
    docs, scoore = retriver.retrieve(query_tokens, k=2, leave_progress=True)
    print(docs)
    print(scoore)
    
    retriver.save("data/processed")
        

if __name__ == "__main__":
    fire.Fire(main)
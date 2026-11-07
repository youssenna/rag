import fire
import tqdm
import ast
import pathlib
# from .pipline import Pipline
from typing import List
from .index import PyFileChunker




def main():
    py_chunker = PyFileChunker('src/pipline.py', 500)
    py_chunker.get_chunks()
        

if __name__ == "__main__":
    fire.Fire(main)
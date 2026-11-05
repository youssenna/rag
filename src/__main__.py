import fire
import tqdm
import ast
import pathlib
# from .pipline import Pipline
from typing import List
from .index import PyFileChunker




def main():
    py_chunker = PyFileChunker('src/pipline.py')
    for chunk in py_chunker.get_chunks():
        print('#'*100)
        print(chunk, end='')
    
        

if __name__ == "__main__":
    fire.Fire(main)
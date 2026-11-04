import fire
import tqdm
import ast
import pathlib
# from .pipline import Pipline
from typing import List


class PyFileChunker:
    def __init__(self, file_path: str, max_chunk_size: int = 2000):
        self.file_path: str = file_path
        self.max_chunk_size: str = max_chunk_size
        self._file_content: str = self._get_file_content()
        # self._lines_start will store the index of the first charcter 
        # of every line in the file
        self._lines_start: List[int] = self._get_starts()

    def _get_file_content(self) -> str:
        with open(self.file_path, 'r') as f:
            content = f.read()
        return content

    def _get_starts(self) -> List[int]:
        lines_start = [0]

        for line in self._file_content.splitlines(keepends=True):
            lines_start.append(lines_start[-1] + len(line))
        return lines_start

    def _get_chunk(self, first_line: int, last_line: int) -> str:
        start_index = self._lines_start[first_line-1]
        end_index = self._lines_start[last_line]
        return self._file_content[start_index: end_index]

    def get_chunks(self) -> List[str]:
        print("#"*100)
        tree = ast.parse(self._file_content)
        for node in tree.body:
            print(type(node).__name__, node.lineno, node.end_lineno)
            if isinstance(node, ast.ClassDef):
                print('-'*30)
                for nod in node.body:
                    print(type(nod).__name__, nod.lineno, nod.end_lineno)
                    # if isinstance(nod, ast.FunctionDef):
                    #     print('*'*30)
                    #     print(nod.name, nod.lineno, nod.end_lineno)
        # print(ast.dump(tree, indent=2))
        
        print("#"*100)
        for node in tree.body:
            print(node, node.lineno, node.end_lineno)


def main():
    py_chunker = PyFileChunker('src/pipline.py')
    for chunk in py_chunker.get_chunks():
        print('#'*100)
        print(chunk, end='')
    
        

if __name__ == "__main__":
    fire.Fire(main)
from .utils import MinimalSource, Chunk

from typing import List, Self
from pathlib import Path
from json import dump
import ast


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
    def _split_line_to_chunks(self, line, last_index: int):
        chunks: List[Chunk] = []
        buffer = ''
        chunk_start = 0
        chunk_end  = self.max_chunk_size
        while chunk_end < len(line):
            buffer = line[chunk_start:chunk_end]
            chunks.append(Chunk(file_path=self.file_path,
                                text_content=buffer,
                                first_character_index=last_index+chunk_start,
                                last_character_index=last_index+chunk_end))
            chunk_start = chunk_end
            chunk_end += self.max_chunk_size
            last_index += self.max_chunk_size

        if line[chunk_start:]:
            buffer = line[chunk_start:]
            chunks.append(Chunk(file_path=self.file_path,
                                text_content=buffer,
                                first_character_index=chunk_start,
                                last_character_index=chunk_start+len(buffer)))
            last_index += len(buffer)
        return chunks, last_index
            
        
    def get_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        buffer = ''
        print(self._file_content.splitlines(keepends=True))
        print('#'*30)
        line_num = 1
        last_index = 0
        for line in self._file_content.splitlines(keepends=True):
            if len(line) > self.max_chunk_size:
                parts, last_index = self._split_line_to_chunks(line, last_index)
                chunks.extend(parts)
            elif len(buffer) > self.max_chunk_size:
                chunk: Chunk = Chunk(file_path=self.file_path,
                              text_content=buffer,
                              first_character_index=last_index,
                              last_character_index=last_index+len(buffer))
                chunks.append(chunk)
                last_index += len(buffer)
                buffer = line
                
            elif len(buffer) + len(line) <= self.max_chunk_size:
                buffer += line
        if buffer:
            chunks.append(Chunk(file_path=self.file_path,
                          text_content=buffer,
                          first_character_index=last_index,
                          last_character_index=last_index+len(buffer)))
            # print(line)
            # if len(buffer) + len(line) <= self.max_chunk_size:
            #     buffer += line
            # else:
            #     chunk: Chunk = Chunk(file_path=self.file_path,
            #                   text_content=buffer,
            #                   first_character_index=last_index,
            #                   last_character_index=last_index+len(buffer))
            #     chunks.append(chunk)
            #     last_index += len(buffer)
            #     buffer = line
        # if line:
            

        for chunk_ in chunks:
            print(chunk_.text_content, end='')  


class Index:
    def __init__(self, max_chunk_size: int = 2000) -> Self:
        self.max_chunk_size: int = max_chunk_size
        
    def run(self):
        chunks: List[MinimalSource] = []
        saved_dir = Path('data/processed/')
        saved_file = Path('data/processed/chunks.json')
        root_folder = Path("data/raw/vllm-0.10.1")
        for py_file in root_folder.rglob('*.py'):
            with open(py_file, 'r') as f:
                chunks.extend(self._chunk_file(f, py_file, len(chunks)))
        
        saved_dir.mkdir(parents=True, exist_ok=True)
        saved_file.touch(exist_ok=True)
        
        json_str = [chunk.__dict__ for chunk in chunks]
        print(json_str)
        with open(saved_file, 'w') as f:
            dump(json_str, f, indent=4)
            
        print('Ingestion complete! Indices saved under data/processed/')

    def _chunk_file(self, f, path: str, chunks_len: int) -> List[MinimalSource]:
        file_chunks: List[MinimalSource] = []
        first_chr_index = 0
        last_chr_index = 0
        while chunk_str:= f.read(self.max_chunk_size):
            last_chr_index = first_chr_index + (len(chunk_str) - 1)
            # print(path)
            minimal_source = Chunk(file_path=str(path),
                                   first_character_index=first_chr_index,
                                   last_character_index=last_chr_index,
                                   chunk_id=(chunks_len+len(file_chunks)),
                                   text_content=chunk_str)
            # minimal_source.file_path = path
            # minimal_source.first_character_index = first_chr_index
            # minimal_source.last_character_index = last_chr_index
            first_chr_index += len(chunk_str)
            file_chunks.append(minimal_source)
        return file_chunks
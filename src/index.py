from .utils import MinimalSource, Chunk

from typing import List, Tuple, Dict
from pathlib import Path
from json import dump
import ast
from abc import ABC, abstractmethod
import re



class FileChunker:
    def __init__(self, file_path: str, max_chunk_size: int = 2000):
        self.file_path: str = file_path
        self.max_chunk_size: int = max_chunk_size
        self._file_content: str = self._get_file_content()
        # self._lines_start will store the index of the first charcter 
        # of every line in the file
        self._lines_start: List[int] = self._get_starts()
                
    def _get_file_content(self) -> str:
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
               
    def _get_starts(self) -> List[int]:
        lines_start = [0]

        for line in self._file_content.splitlines(keepends=True):
            lines_start.append(lines_start[-1] + len(line))
        return lines_start


    @staticmethod
    def _tokonization(s: str) -> List[str]:
        return re.findall(r"[\da-zA-Z]+", s.lower())
    
    def _tokens_repetition(self, text_to_tokens: List[str], text_tokens: List[str]) -> Dict[str, int]:
        result: Dict[str] = self._initial_repetition(text_tokens)
        for token in text_tokens:
            while token in text_to_tokens:
                text_to_tokens.remove(token)
                result[token] += 1
        return result
            
    @staticmethod
    def _initial_repetition(tokens: List[str]) -> Dict[str, int]:
        return {token: 0 for token in tokens}
        
    @abstractmethod
    def get_chunks(self) -> List[Chunk]:
        pass


class MdFileChunker(FileChunker):
    def _split_line_to_chunks(self, line, last_index: int) -> Tuple[List[Chunk], int]:
        chunks: List[Chunk] = []
        buffer = ''
        chunk_start = 0
        chunk_end  = self.max_chunk_size
        while chunk_end < len(line):
            buffer = line[chunk_start:chunk_end]
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index+chunk_start,
                                last_character_index=last_index+chunk_end - 1,
                                text_content=buffer,
                                tokens_len=len(text_to_tokens),
                                repetition=self._tokens_repetition(
                                    text_to_tokens,
                                    list(set(text_to_tokens))))
                          )

            chunk_start = chunk_end
            chunk_end += self.max_chunk_size

        if line[chunk_start:]:
            buffer = line[chunk_start:]
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index + chunk_start,
                                last_character_index=last_index + chunk_start+len(buffer) - 1,
                                text_content=buffer,
                                tokens_len=len(text_to_tokens),
                                repetition=self._tokens_repetition(
                                    text_to_tokens,
                                    list(set(text_to_tokens))))
                          )

        return chunks, last_index + len(line)
            
        
    def get_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        buffer = ''
        last_index = 0
        for line in self._file_content.splitlines(keepends=True):
            if len(buffer) + len(line) > self.max_chunk_size:
                if buffer:
                    
                    text_to_tokens = self._tokonization(buffer)
                    chunks.append(Chunk(file_path=self.file_path,
                                  first_character_index=last_index,
                                  last_character_index=last_index+len(buffer) - 1,
                                  text_content=buffer,
                                  tokens_len=len(text_to_tokens),
                                  repetition=self._tokens_repetition(
                                    text_to_tokens,
                                    list(set(text_to_tokens))))
                                  )
                    last_index += len(buffer)
                    buffer = ''
                
            if len(line) > self.max_chunk_size:
                parts, last_index = self._split_line_to_chunks(line, last_index)
                chunks.extend(parts)
            else:
                buffer += line
      
        if buffer:
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                          first_character_index=last_index,
                          last_character_index=last_index+len(buffer) - 1,
                          text_content=buffer,
                          tokens_len=len(text_to_tokens),
                          repetition=self._tokens_repetition(
                            text_to_tokens,
                            list(set(text_to_tokens))))
                          )
        return chunks
            
    

class PyFileChunker(FileChunker):
    def _split_line_to_chunks(self, line, last_index: int) -> Tuple[List[Chunk], int]:
        chunks: List[Chunk] = []
        buffer = ''
        chunk_start = 0
        chunk_end  = self.max_chunk_size
        while chunk_end < len(line):
            buffer = line[chunk_start:chunk_end]
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index+chunk_start,
                                last_character_index=last_index+chunk_end - 1,
                                text_content=buffer,
                                tokens_len=len(text_to_tokens),
                                repetition=self._tokens_repetition(
                                    text_to_tokens,
                                    list(set(text_to_tokens))))
                          )
            chunk_start = chunk_end
            chunk_end += self.max_chunk_size

        if line[chunk_start:]:
            buffer = line[chunk_start:]
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index + chunk_start,
                                last_character_index=last_index + chunk_start+len(buffer) - 1,
                                text_content=buffer,
                                tokens_len=len(text_to_tokens),
                                repetition=self._tokens_repetition(
                                    text_to_tokens,
                                    list(set(text_to_tokens))))
                          )
        return chunks, last_index + len(line)
            
        
    def get_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        buffer = ''
        last_index = 0
        for line in self._file_content.splitlines(keepends=True):
            if len(buffer) + len(line) > self.max_chunk_size:
                if buffer:
                    text_to_tokens = self._tokonization(buffer)
                    chunks.append(Chunk(file_path=self.file_path,
                                  first_character_index=last_index,
                                  last_character_index=last_index+len(buffer) - 1,
                                  text_content=buffer,
                                  tokens_len=len(text_to_tokens),
                                  repetition=self._tokens_repetition(
                                      text_to_tokens,
                                      list(set(text_to_tokens))))
                                  )
                    last_index += len(buffer)
                    buffer = ''
                
            if len(line) > self.max_chunk_size:
                parts, last_index = self._split_line_to_chunks(line, last_index)
                chunks.extend(parts)
            else:
                buffer += line
      
        if buffer:
            text_to_tokens = self._tokonization(buffer)
            chunks.append(Chunk(file_path=self.file_path,
                          first_character_index=last_index,
                          last_character_index=last_index+len(buffer) - 1,
                          text_content=buffer,
                          tokens_len=len(text_to_tokens),
                          repetition=self._tokens_repetition(
                                text_to_tokens,
                                list(set(text_to_tokens))))
                          )
        return chunks   


class Index:
    def __init__(self, max_chunk_size: int = 2000) -> None:
        self.max_chunk_size: int = max_chunk_size
        
    def run(self):
        chunks: List[Chunk] = []
        saved_dir = Path('data/processed/')
        saved_file = Path('data/processed/chunks.json')
        root_folder = Path("data/raw/vllm-0.10.1")
        for py_file in root_folder.rglob('*.py'):
            # with open(py_file, 'r') as f:
            file_chunks = PyFileChunker(str(py_file), self.max_chunk_size)
            chunks.extend(file_chunks.get_chunks())
        for md_file in root_folder.rglob('*.md'):
            file_chunks = MdFileChunker(str(md_file), self.max_chunk_size)
            chunks.extend(file_chunks.get_chunks())
        saved_dir.mkdir(parents=True, exist_ok=True)
        saved_file.touch(exist_ok=True)
        
        json_str = [chunk.model_dump() for chunk in chunks]
        # print(json_str)
        with open(saved_file, 'w') as f:
            dump(json_str, f, indent=4)
            
        print('Ingestion complete! Indices saved under data/processed/')

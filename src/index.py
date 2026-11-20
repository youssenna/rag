from .utils import MinimalSource, Chunk

from langchain_community.document_loaders import PythonLoader, DirectoryLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.documents import Document



from typing import List, Tuple, Dict
from pathlib import Path
from json import dump
import ast
from abc import ABC, abstractmethod
import re
import bm25s



class FileChunker(ABC):
    def __init__(self, file_path: str, max_chunk_size: int = 2000):
        self.file_path: str = file_path
        self.max_chunk_size: int = max_chunk_size
        # self._lines_start will store the index of the first charcter 
        # of every line in the file
                



        
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
            
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index+chunk_start,
                                last_character_index=last_index+chunk_end - 1,
                                text_content=buffer)
                          )

            chunk_start = chunk_end
            chunk_end += self.max_chunk_size

        if line[chunk_start:]:
            buffer = line[chunk_start:]
            
            chunks.append(Chunk(file_path=self.file_path,
                                first_character_index=last_index + chunk_start,
                                last_character_index=last_index + chunk_start+len(buffer) - 1,
                                text_content=buffer)
                          )

        return chunks, last_index + len(line)
            
        
    def get_chunks(self) -> List[Chunk]:
        chunks: List[Chunk] = []
        buffer = ''
        last_index = 0
        for line in self._file_content.splitlines(keepends=True):
            if len(buffer) + len(line) > self.max_chunk_size:
                if buffer:
                    
                    
                    chunks.append(Chunk(file_path=self.file_path,
                                  first_character_index=last_index,
                                  last_character_index=last_index+len(buffer) - 1,
                                  text_content=buffer)
                                  )
                    last_index += len(buffer)
                    buffer = ''
                
            if len(line) > self.max_chunk_size:
                parts, last_index = self._split_line_to_chunks(line, last_index)
                chunks.extend(parts)
            else:
                buffer += line
      
        if buffer:
            
            chunks.append(Chunk(file_path=self.file_path,
                          first_character_index=last_index,
                          last_character_index=last_index+len(buffer) - 1,
                          text_content=buffer)
                          )
        return chunks
            
    

class PyFileChunker(FileChunker):
    
    def _get_chunks_from_decoment(self, document: Document) -> List[Chunk]:
        chunks: List[Chunk] = []
        python_spliter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON,
                                                                      chunk_size=self.max_chunk_size,
                                                                      chunk_overlap=self.max_chunk_size // 10,
                                                                      add_start_index=True)
        documents = python_spliter.split_documents([document])
        for doc in documents:
            start_index = doc.metadata['start_index']
            last_index = doc.metadata['start_index'] + len(doc.page_content) - 1
            
            chunks.append(Chunk(file_path=doc.metadata['source'],
                                first_character_index=start_index,
                                last_character_index=last_index,
                                text_content=doc.page_content))
            document.metadata['source']
        return chunks
    
    def get_chunks(self) -> List[Chunk]:
        py_loader = DirectoryLoader(path='data/raw/vllm-0.10.1',
                                 glob='**/*.py',
                                 loader_cls=PythonLoader,
                                 show_progress=True)
        py_documents = py_loader.load()
        
        
        chunks: List[Chunk] = []
        
        for document in py_documents:
            chunks.extend(self._get_chunks_from_decoment(document))
        return chunks


class Index:
    def __init__(self, max_chunk_size: int = 2000) -> None:
        self.max_chunk_size: int = max_chunk_size
        
    def run(self):
        # py_loader = DirectoryLoader(path='data/raw/vllm-0.10.1',
        #                          glob='**/*.py',
        #                          loader_cls=PythonLoader,
        #                          show_progress=True)
        # py_decoments = py_loader.load()
        # md_loader = DirectoryLoader(path='data/raw/vllm-0.10.1',
        #                             glob='**/*.md',
        #                             loader_cls=UnstructuredMarkdownLoader,
        #                             show_progress=True)
        # md_decoments = md_loader.load()
        # # for dec in md_decoments:
        # #     print(dec.page_content)
            
        # python_spliter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON,
        #                                                               chunk_size=self.max_chunk_size,
        #                                                               chunk_overlap=self.max_chunk_size // 10,
        #                                                               add_start_index=True)
        
        # chunks = python_spliter.split_documents(PythonLoader('data/raw/vllm-0.10.1/setup.py').load())
        # print(chunks)
        chunks: List[Chunk] = []
        saved_dir = Path('data/processed')
        saved_file = Path('data/processed/chunks.json')
        root_folder = Path("data/raw/vllm-0.10.1")
        
        python_chunker = PyFileChunker(root_folder, self.max_chunk_size)
        chunks.extend(python_chunker.get_chunks())

        # for md_file in root_folder.rglob('*.md'):
        #     file_chunks = MdFileChunker(str(md_file), self.max_chunk_size)
        #     chunks.extend(file_chunks.get_chunks())
        saved_dir.mkdir(parents=True, exist_ok=True)
        saved_file.touch(exist_ok=True)
        
        json_str = [chunk.model_dump() for chunk in chunks]
        # print(json_str)
        corpus = [chunk.text_content for chunk in chunks]
        corpus_tokens = bm25s.tokenize(corpus)
        
        retrive = bm25s.BM25()
        retrive.index(corpus_tokens, leave_progress=True)
        retrive.save('data/processed/index/')
        
        with open(saved_file, 'w') as f:
            dump(json_str, f, indent=4)
        
            
        print('Ingestion complete! Indices saved under data/processed/')

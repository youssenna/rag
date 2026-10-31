from .utils import MinimalSource

from typing import List, Self
from pathlib import Path
from json import dump



class Chunk(MinimalSource):
    chunk_id: int
    text_content: str

class Index:
    def __init__(self, max_chunk_size: int = 2000) -> Self:
        self.max_chunk_size: int = max_chunk_size
        
    def run(self):
        print("fuck you")
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
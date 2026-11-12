from .errors import SearchDatasetError
from .search import Search
from .utils import UnansweredQuestion, StudentSearchResults

from pathlib import Path
from typing import List
import json

class SearchDataset:
    def __init__(self, dataset_path: str, k: int, save_directory: str):
        self.dataset_path: str = dataset_path
        self.k: int = k
        self.save_directory: str = save_directory
        
        
    def run(self):
        try:
            dataset = Path(self.dataset_path)
            result: List[StudentSearchResults] = []
            with open(dataset, 'r', encoding='utf-8') as dataset_file:
                result_dir_path = Path(self.save_directory)
                # print(dataset.name)
                result_file_path = Path(self.save_directory+'/'+dataset.name)
                result_dir_path.mkdir(parents=True, exist_ok=True)
                result_file_path.touch()
                questions: List[UnansweredQuestion] = json.load(dataset_file)
                # print(questions)
                # i need to fix something her
                for question in questions:
                    search_results = Search(question.question, self.k, question['question_id'])
                    result.append(StudentSearchResults(search_results=search_results.run(), k=self.k))
                
                
                print("Saved student_search_results to", result_file_path)
        except FileNotFoundError:
            raise SearchDatasetError(f'file {self.dataset_path}',
                                     'not found it, make sure the file exist')
        except PermissionError:
            raise SearchDatasetError(f'premssion denided: make sure you have the right ',
                                     f'access to the [{self.dataset_path}] file')

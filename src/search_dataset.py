from .errors import SearchDatasetError
from .search import Search
from .utils import UnansweredQuestion, StudentSearchResults, MinimalSearchResults

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
            result: List[MinimalSearchResults] = []
            with open(dataset, 'r', encoding='utf-8') as dataset_file:
                result_dir_path = Path(self.save_directory)
                # print(dataset.name)
                result_file_path = Path(self.save_directory+'/'+dataset.name)
                result_dir_path.mkdir(parents=True, exist_ok=True)
                result_file_path.touch()
                questions: List[UnansweredQuestion] = json.load(dataset_file)
                # print(questions)
                # i need to fix something her
                for q in questions["rag_questions"]:
                    print(q)
                    print(q['question_id'])
                    search_results = Search(q['question'], self.k, q['question_id'])
                    result.append(MinimalSearchResults(question_id=q['question_id'],
                                                       question= q['question'],
                                                       retrieved_sources=search_results.run(debug=False)))
                with open(result_file_path, 'w') as output_file:
                    
                    student_search_result = StudentSearchResults(search_results=result, k=self.k)
                    json.dump(student_search_result.model_dump(), output_file, indent=4)
                print("Saved student_search_results to", result_file_path)
        except FileNotFoundError:
            raise SearchDatasetError(f'file {self.dataset_path}',
                                     'not found it, make sure the file exist')
        except PermissionError:
            raise SearchDatasetError(f'premssion denided: make sure you have the right ',
                                     f'access to the [{self.dataset_path}] file')

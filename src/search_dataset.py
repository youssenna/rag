from pathlib import Path
from .errors import SearchDatasetError

class SearchDataset:
    def __init__(self, student_search_results_path: str, k: int, save_directory: str):
        self.student_search_results_path: str = student_search_results_path
        self.k: int = k
        self.save_directory: str = save_directory
        
        
    def run(self):
        try:
            with open(self.student_search_results_path, 'r', encoding='utf-8'):
                result_dir_path = Path(self.save_directory)
                result_file_path = Path(self.save_directory+'search_dataset.json')
                result_dir_path.mkdir(parents=True, exist_ok=True)
                result_file_path.touch()
                
                print("Saved student_search_results to", result_file_path)
        except FileNotFoundError:
            raise SearchDatasetError(f'file {self.student_search_results_path}',
                                     'not found it, make sure the file exist')
        except PermissionError:
            raise SearchDatasetError(f'premssion denided: make sure you have the right ',
                                     f'access to the [{self.student_search_results_path}] file')

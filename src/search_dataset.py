from pathlib import Path

class SearchDataset:
    def __init__(self, student_search_results_path: str, k: int, save_directory: str):
        self.student_search_results_path: str = student_search_results_path
        self.k: int = k
        self.save_directory: str = save_directory
        
        
    def run(self):
        dir_path = Path(self.save_directory)
        file_path = Path(self.student_search_results_path)
        print(file_path.parent, '=', dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
        file_path.touch(exist_ok=True)
        print("Saved student_search_results to", file_path)
import subprocess
from .errors import EvaluateError


class Evaluate:
    def __init__(self,
                 student_search_results_path: str,
                 dataset_path: str,
                 k: int, max_context_length: int) -> None:
        self.student_search_results_path: str = student_search_results_path
        self.dataset_path: str = dataset_path
        self.k: int = k
        self.max_context_length: int = max_context_length
        
        
    def run(self):
        try:
            command = str('./moulinette evaluate_student_search_results'+
                           f' {self.student_search_results_path}'+
                           f' {self.dataset_path}'+
                           f' {self.k}'+
                           f' {self.max_context_length}')
            res = subprocess.run(command,
                                 shell=True,
                                 capture_output=True,
                                 text=True,
                                 check=True
                                 )
            print(res.stdout)
        except subprocess.CalledProcessError as e:
            raise EvaluateError(e.stderr)
        # print(res.stderr)
    
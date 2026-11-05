from pathlib import Path
from .utils import MinimalSource
from .errors import *
from .index import Index
from .search import Search
from .search_dataset import SearchDataset
from .answer import Answer
from .answer_dataset import AnswerDataset
from .evaluate import Evaluate

class Pipline:
    def index(self, max_chunk_size: int = 2000):
        index_obj = Index(max_chunk_size)
        index_obj.run()
        

    def search(self, query: str, k: int):
        search_obj = Search(query=query, k=k)
        search_obj.run()
    
    def search_dataset(self, student_search_results_path: str, k: int, save_directory: str):
        search_dataset_obj = SearchDataset(student_search_results_path, k, save_directory)
        search_dataset_obj.run()
        

    def answer(self, query: str, k: int):
        answer_obj = Answer(query, k)
        answer_obj.run()


    def answer_dataset(self, student_search_results_path: str, save_directory: str):
        answer_dataset_obj = AnswerDataset(student_search_results_path, save_directory)
        answer_dataset_obj.run()

    def evaluate(self, student_search_results_path: str, dataset_path: str):
        evaluate_obj = Evaluate(student_search_results_path, dataset_path)
        evaluate_obj.run()

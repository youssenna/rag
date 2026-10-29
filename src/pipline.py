class Pipline:
    def index(self, max_chunk_size: int = 2000):
        print("hello from index", max_chunk_size)

    def search(self, query: str, k: int):
        pass

    def answer(self, query: str, k: int):
        pass


    def answer_dataset(self, student_search_results_path: str, save_directory: str):
        pass

    def evaluate(self, student_search_results_path: str, dataset_path: str):
        pass

from .answer import Answer
from .utils import StudentSearchResultsAndAnswer, MinimalAnswer

from transformers import AutoModelForCausalLM, AutoTokenizer
from pathlib import Path
from json import load, dump
from typing import List

class AnswerDataset:
    def __init__(self, student_search_results_path: str, save_directory: str):
        self.student_search_results_path: str = student_search_results_path
        self.save_directory: str = save_directory
        # self.tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
        # self.model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-0.6B')
        
    @staticmethod
    def _get_retrieved_sources(sources):
        result = ''
        for index, retrieved in enumerate(sources):
            result += f'chunk number {str(index+1)}:\n'
            with open(retrieved['file_path'], 'r') as file_path:
                result += file_path.read()[
                    retrieved['first_character_index']:retrieved['last_character_index']]
                
        return result

    def run(self):
        save_directory = Path(self.save_directory)
        src_file = Path(self.student_search_results_path)
        save_directory.mkdir(parents=True, exist_ok=True)
        save_file = Path(str(save_directory) +'/'+ src_file.name)
        save_file.touch()
        answers: List[MinimalAnswer] = []
        prompt  = '''
You are an assistant that answers questions
about a software project.

Use only the provided context to answer.
If the context does not contain the answer,
say that you don't know.

Context:
'''
        
        
        with open(Path(self.student_search_results_path), 'r', encoding='utf-8') as student_search_file:
            src_obj = load(student_search_file)
            # print(src_obj)    
            k = src_obj['k']
            for index, q in enumerate(src_obj['search_results']):
                query = prompt + self._get_retrieved_sources(q['retrieved_sources'])
                query += f'\nQuestion {index +1}:\n{q['question']}\nAnswer:\n'
                answer_obj = Answer(query=query,
                                    k=k)
                answers.append(MinimalAnswer(question_id=q['question_id'],
                                             question=q['question'],
                                             retrieved_sources=q['retrieved_sources'],
                                             answer=answer_obj.run()))
        result = StudentSearchResultsAndAnswer(search_results=answers, k=k)    
        with open(save_file, 'w') as save_f:
            dump(result.model_dump(), save_f, indent=4)
        return StudentSearchResultsAndAnswer(search_results=answers, k=k)        
                
        
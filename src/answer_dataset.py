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
        self.tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
        self.model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-0.6B')
        
    @staticmethod
    def _get_retrieved_sources(sources):
        result = 'Context:\n'
        for index, retrieved in enumerate(sources):
            result += '\n' + '#'*30 + f' chunk number {str(index+1)} ' + '#'*30 + '\n'
            with open(retrieved['file_path'], 'r') as file_path:
                result += file_path.read()[
                    retrieved['first_character_index']:retrieved['last_character_index']]
                
        return result

    def _get_answer(self, context_and_question: str):
        system_mesg = '''
- You are an assistant that answers questions about a software project.
- You will recive provided context and you should use it as referece to answer the given question.
- if the provided context does not have the answer to the question mention that in the answer, and give don't answer outside the provided context
'''
        messages = [
                    {
                        "role": "system",
                        "content": system_mesg
                    },
                    {
                        "role": "user",
                        "content": context_and_question
                    }
        ]
        tokenized_chat = self.tokenizer.apply_chat_template(messages,
                                                        tokenize=True,
                                                        add_generation_prompt=True,
                                                        return_tensors='pt',
                                                        add_special_tokens=False,
                                                        enable_thinking=False).to(self.model.device)
        output = self.model.generate(**tokenized_chat, max_new_tokens=120)
        input_len = tokenized_chat['input_ids'].shape[-1]
        answer = self.tokenizer.decode(output[0][input_len:], skip_special_tokens=True)
        # print(answer)
        return answer

    def run(self):
        save_directory = Path(self.save_directory)
        src_file = Path(self.student_search_results_path)
        save_directory.mkdir(parents=True, exist_ok=True)
        save_file = Path(str(save_directory) +'/'+ src_file.name)
        save_file.touch()
        answers: List[MinimalAnswer] = []
        
    
        with open(Path(self.student_search_results_path), 'r', encoding='utf-8') as student_search_file:
            src_obj = load(student_search_file)
            # print(src_obj)
            k = src_obj['k']
            for index, q in enumerate(src_obj['search_results']):
                query = self._get_retrieved_sources(q['retrieved_sources'])
                query += f'\nQuestion {index +1}:\n{q['question']}\n'
                answers.append(MinimalAnswer(question_id=q['question_id'],
                                             question=q['question'],
                                             retrieved_sources=q['retrieved_sources'],
                                             answer=self._get_answer(query)))
                # return 
        result = StudentSearchResultsAndAnswer(search_results=answers, k=k)    
        with open(save_file, 'w') as save_f:
            dump(result.model_dump(), save_f, indent=4)
        return StudentSearchResultsAndAnswer(search_results=answers, k=k)        
                
        
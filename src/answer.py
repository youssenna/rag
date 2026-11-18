from typing import List

from .search import Search
from .utils import MinimalSource

from transformers import AutoModelForCausalLM, AutoTokenizer

# from .utils import MinimalAnswer

class Answer:
    def __init__(self, query: str, k: int):
        self.query: str = query
        self.k: int = k
        
        
    def _get_provided_context(self):
        search = Search(self.query, self.k)
        result: List[MinimalSource] = search.run()
        context = '- Context:\n'
        for index, retrieved in enumerate(result):
            context += '\n' + '#'*30 + f' chunk number {str(index+1)} ' + '#'*30 + '\n'
            with open(retrieved.file_path, 'r') as file_path:
                context += file_path.read()[
                    retrieved.first_character_index:retrieved.last_character_index]
        return context
        
    def run(self) -> str:
        # print('#'*30, 'question', '#'*30)
        tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
        model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-0.6B')
        system_mesg = '''
- You are an assistant that answers questions about a software project.
- You will recive provided context and you should use it as referece to answer the given question.
'''
        
        user_mesg = self._get_provided_context()
        user_mesg += '\n\n' + '#'*30 + ' Question ' + '#'*30
        user_mesg += f'\n{self.query}'
        print(user_mesg)
        # return 
        
        messages = [
            {
                "role": "system",
                "content": system_mesg
            },
            {
                "role": "user",
                "content": user_mesg
            }
        ]
        tokenized_chat = tokenizer.apply_chat_template(messages,
                                                       tokenize=True,
                                                       add_generation_prompt=True,
                                                       return_tensors='pt',
                                                       add_special_tokens=False,
                                                       enable_thinking=False).to(model.device)
        output = model.generate(**tokenized_chat, max_new_tokens=120)
        input_len = tokenized_chat['input_ids'].shape[-1]
        answer = tokenizer.decode(output[0][input_len:], skip_special_tokens=True)
        print(answer)
        return answer
        
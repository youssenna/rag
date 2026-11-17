from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# from .utils import MinimalAnswer

class Answer:
    def __init__(self, query: str, k: int):
        self.query: str = query
        self.k: int = k
        
        
    def run(self) -> str:
        print('#'*30, 'question', '#'*30)
        print(self.query)
        tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
        model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-0.6B')
        chat = [
            {"role": "system", "content": "You are a helpful science assistant."},
            {"role": "user", "content": "is abchtaib low iqu?"}
        ]

        pipelin = pipeline(task="text-generation", model="Qwen/Qwen3-0.6B", dtype="auto", device_map="auto")
        response = pipelin(chat, max_new_tokens=512)
        print(response[0]["generated_text"][-1]["content"])
        # input_ids = tokenizer.encode(self.query, return_tensors='pt', enable_thinking=False, do_sample=False)
        # output = model.generate(input_ids, eos_token_id=tokenizer.eos_token_id)
        # new_tokens = output[0][input_ids.shape[-1]:]
        # answer = tokenizer.decode(new_tokens, skip_special_tokens=True)
        # tokenizer.decode(output[0], skip_special_tokens=True)
        # print('#'*30, 'answer', '#'*30)
        # print(answer)
        # return answer
        
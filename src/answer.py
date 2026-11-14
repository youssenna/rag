from transformers import AutoModelForCausalLM, AutoTokenizer


class Answer:
    def __init__(self, query: str, k: int):
        self.query: str = query
        self.k: int = k
        
        
    def run(self):
        tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen3-0.6B')
        model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen3-0.6B')
        input_ids = tokenizer.encode("Once upon a time,", return_tensors='tf')
        output = model.generate(input_ids)
        print(tokenizer.decode(output[0], skip_special_tokens=True))
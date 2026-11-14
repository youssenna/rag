<b>This project has been created as part of the 42 curriculum by yousenna</b>
# how to run the project step by step.

## run index command with 2000 in max_chunk_size

```sh
uv run -m src index --max_chunk_size=2000
```


## retrive code and docs dataset
### run search_dataset command for code dataset

```sh
uv run -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_code_public.json --k 10 --save_directory data/output/search_results/UnansweredQuestions
```

### run search_dataset command for docs dataset


```sh
uv run -m src search_dataset --dataset_path data/datasets/UnansweredQuestions/dataset_docs_public.json --k 10 --save_directory data/output/search_results/UnansweredQuestions
```

## Evaluation:
### evaluate code dataset:
``` sh
uv run -m src evaluate \
data/output/search_results/UnansweredQuestions/dataset_code_public.json \
data/datasets/AnsweredQuestions/dataset_code_public.json --k 10 --max_context_length 2000
```

### evaluate docs dataset:
``` sh
uv run -m src evaluate \
data/output/search_results/UnansweredQuestions/dataset_docs_public.json \
data/datasets/AnsweredQuestions/dataset_docs_public.json --k 10 --max_context_length 2000
```


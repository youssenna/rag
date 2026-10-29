import fire
import tqdm
import ast
import pathlib
from .pipline import Pipline



def main():
    root = pathlib.Path("data/raw/vllm-0.10.1/")
    for path in root.rglob("*.md"):
        print(path)

if __name__ == "__main__":
    fire.Fire(main)
    fire.Fire(Pipline)
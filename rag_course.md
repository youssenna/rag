# 🎓 The Complete RAG Course — Your Project, Explained

> **Project**: Build a RAG (Retrieval-Augmented Generation) system over the **vLLM 0.10.1** codebase.
> Your goal: given a question about vLLM's code, find the exact file and character range that answers it.

---

## 📚 Table of Contents

1. [What is RAG? The Big Picture](#1-what-is-rag-the-big-picture)
2. [Your Project's Goal — Explained Simply](#2-your-projects-goal--explained-simply)
3. [Step 1 — Chunking: Slicing the Knowledge Base](#3-step-1--chunking-slicing-the-knowledge-base)
4. [Step 2 — Embeddings: Turning Text into Numbers](#4-step-2--embeddings-turning-text-into-numbers)
5. [Step 3 — Vector Store: The Smart Library Index](#5-step-3--vector-store-the-smart-library-index)
6. [Step 4 — Retrieval: Finding the Right Piece](#6-step-4--retrieval-finding-the-right-piece)
7. [Step 5 — Evaluation: How Do You Know It Works?](#7-step-5--evaluation-how-do-you-know-it-works)
8. [Your Dataset — What You're Working With](#8-your-dataset--what-youre-working-with)
9. [Your Evaluation System (the Moulinette)](#9-your-evaluation-system-the-moulinette)
10. [The Full Pipeline at a Glance](#10-the-full-pipeline-at-a-glance)
11. [Key Tools & Libraries You'll Use](#11-key-tools--libraries-youll-use)
12. [Common Pitfalls & How to Avoid Them](#12-common-pitfalls--how-to-avoid-them)
13. [Strategy to Beat the Thresholds](#13-strategy-to-beat-the-thresholds)

---

## 1. What is RAG? The Big Picture

### 🧠 The Problem RAG Solves

Imagine you ask a very smart friend: *"What does vLLM's `fused_batched_moe.py` return for activation formats?"*

Your friend is brilliant but they haven't read every single file of vLLM's 500,000+ lines of code. They can't answer. This is the **limitation of a pure LLM** — it only knows what it was trained on, and it can't look things up in real time.

**RAG = Retrieval + Generation**. Instead of relying only on the model's memory, we:
1. 📖 **Retrieve** the most relevant piece of code/text from a large knowledge base
2. 💬 **Generate** an answer using that piece as context

> **Analogy**: RAG is like an open-book exam. Instead of memorizing everything, you know *how to find the right page quickly*.

### 🔄 The RAG Cycle

```
User Question
     │
     ▼
┌────────────────┐
│   RETRIEVAL    │  ← Find the most relevant text chunks
│  (Your Job!)   │
└────────┬───────┘
         │ Top-K relevant chunks
         ▼
┌────────────────┐
│   GENERATION   │  ← LLM reads chunks + question → answer
│   (Optional)   │
└────────────────┘
         │
         ▼
    Final Answer
```

> ⚠️ **Important**: In YOUR project, the main task is the **RETRIEVAL** part. The evaluation system checks if you retrieved the right file/location, not the quality of a generated answer.

---

## 2. Your Project's Goal — Explained Simply

You have:
- 📁 **A codebase**: `vllm-0.10.1/` — the entire vLLM source code (Python files, docs, etc.)
- ❓ **Questions**: e.g., *"What activation formats does the fused batched MoE layer return?"*
- 🎯 **Your task**: For each question, find the exact location in the code that contains the answer

The answer format you need to produce:
```json
{
  "search_results": [
    {
      "question_id": "189c8b8a-...",
      "question": "What activation formats does...",
      "retrieved_sources": [
        {
          "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
          "first_character_index": 28416,
          "last_character_index": 28975
        }
      ]
    }
  ]
}
```

You need to return **up to 10 sources** per question. The evaluation checks if the **correct source is anywhere in your top-5 results** (Recall@5).

---

## 3. Step 1 — Chunking: Slicing the Knowledge Base

### 🍕 What is Chunking?

Before you can search, you need to slice the files into small, searchable pieces called **chunks**.

> **Analogy**: Imagine the vLLM codebase is a giant pizza. You can't eat the whole thing at once — you cut it into slices. Each slice = one chunk.

### Why Not Just Use Entire Files?

| Approach | Problem |
|----------|---------|
| Entire file as one chunk | Too long, loses precision. The answer is buried |
| One character at a time | Too small, no context |
| Smart chunk (e.g., 500 chars) | ✅ Just right — captures a function or block |

### How to Chunk Code

For **code files** (Python), the best strategies are:

#### Strategy A — Fixed-Size Character Chunks
Slice every N characters with overlap:
```
File content: "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
Chunk size: 10, Overlap: 3

Chunk 1: ABCDEFGHIJ  (chars 0–9)
Chunk 2: HIJKLMNOPQ  (chars 7–16)
Chunk 3: OPQRSTUVWX  (chars 14–23)
```

**Overlap is critical!** It makes sure an answer that spans two chunks isn't missed.

#### Strategy B — Function-Level Chunking (AST-based)
Parse Python files using the `ast` module and extract each function/class as its own chunk.

```python
import ast

with open("some_file.py") as f:
    source = f.read()
    
tree = ast.parse(source)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef):
        start = node.lineno
        end = node.end_lineno
        # Extract that function's text
```

> 🏆 **Recommendation for your project**: Use **character-based chunking** since the ground truth is stored as `first_character_index` / `last_character_index`. This makes evaluation straightforward.

### Your Chunking Output

After chunking, you should have something like:
```python
chunks = [
    {
        "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
        "text": "def activation_formats(self):\n    return (mk.FusedMoEActivationFormat.BatchedExperts, ...)",
        "first_character_index": 28416,
        "last_character_index": 28975
    },
    # ... thousands more chunks
]
```

---

## 4. Step 2 — Embeddings: Turning Text into Numbers

### 🔢 What is an Embedding?

An **embedding** is a way to represent text as a list of numbers (a vector) such that similar texts have similar vectors.

> **Analogy**: Think of each chunk of code as a star in the galaxy. Similar stars (chunks about the same topic) cluster together. The vector is the star's coordinates in space.

### How Embeddings Work (Simplified)

```
"What activation formats does MoE return?"
         │
         ▼
   Embedding Model
         │
         ▼
[0.23, -0.51, 0.88, 0.12, ..., 0.34]  ← 768 numbers (for example)
```

The same model also embeds your code chunks:

```
"return (mk.FusedMoEActivationFormat.BatchedExperts...)"
         │
         ▼
   Embedding Model
         │
         ▼
[0.21, -0.49, 0.91, 0.10, ..., 0.32]  ← Very similar vector! ✅
```

### Choosing an Embedding Model

| Model | Speed | Quality | Notes |
|-------|-------|---------|-------|
| `sentence-transformers/all-MiniLM-L6-v2` | ⚡ Fast | Good | Great starting point |
| `BAAI/bge-base-en-v1.5` | Medium | Very Good | Better for code |
| `BAAI/bge-large-en-v1.5` | Slow | Excellent | Best quality |
| `nomic-ai/nomic-embed-text-v1.5` | Medium | Excellent | Long context friendly |
| `Alibaba-NLP/gte-Qwen2-1.5B-instruct` | Slow | State-of-art | If you have GPU |

> 🏆 **Recommendation**: Start with `BAAI/bge-base-en-v1.5` — good balance of speed and quality for code.

### Code Example

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-base-en-v1.5")

# Embed a question
question = "What activation formats does the fused batched MoE layer return?"
question_embedding = model.encode(question)

# Embed chunks (do this once and save!)
chunk_texts = [chunk["text"] for chunk in chunks]
chunk_embeddings = model.encode(chunk_texts, batch_size=64, show_progress_bar=True)
```

---

## 5. Step 3 — Vector Store: The Smart Library Index

### 📚 What is a Vector Store?

After embedding all your chunks, you need to **store them and search efficiently**.

> **Analogy**: A vector store is like a library's card catalog — instead of reading every book, you use the index to jump directly to the right shelf.

### How Similarity Search Works

When you search, the system computes the **similarity** between your question's vector and all chunk vectors. The most similar chunks win.

The most common similarity measure is **cosine similarity**:
- Score = 1.0 → identical meaning
- Score = 0.0 → completely unrelated
- Score = -1.0 → opposite meaning

### Popular Vector Store Libraries

| Library | Best For | Notes |
|---------|----------|-------|
| **FAISS** | Speed, local | Facebook's library, no server needed |
| **ChromaDB** | Simplicity, local | Easy Python API, persistence built-in |
| **Qdrant** | Production | Great features, also runs locally |
| **Weaviate** | Large scale | Docker-based |

> 🏆 **Recommendation**: Use **FAISS** for this project. It's the fastest, runs locally, and is battle-tested.

### FAISS Example

```python
import faiss
import numpy as np

# Your chunk embeddings: shape (num_chunks, embedding_dim)
embeddings = np.array(chunk_embeddings).astype("float32")

# Build an index
dimension = embeddings.shape[1]  # e.g., 768
index = faiss.IndexFlatIP(dimension)  # IP = Inner Product (cosine if normalized)

# Normalize for cosine similarity
faiss.normalize_L2(embeddings)
index.add(embeddings)

# --- Later, at search time ---
question_vec = model.encode([question]).astype("float32")
faiss.normalize_L2(question_vec)

# Search: get top 10 results
k = 10
distances, indices = index.search(question_vec, k)

# `indices` contains the chunk indices of the top-10 matches
top_chunks = [chunks[i] for i in indices[0]]
```

### Saving and Loading the Index

```python
# Save (do this ONCE after building)
faiss.write_index(index, "vllm_index.faiss")
import json
with open("chunks.json", "w") as f:
    json.dump(chunks, f)

# Load (every time you run search)
index = faiss.read_index("vllm_index.faiss")
with open("chunks.json") as f:
    chunks = json.load(f)
```

---

## 6. Step 4 — Retrieval: Finding the Right Piece

### 🔍 The Retrieval Process

```
Question: "What activation formats does the MoE layer return?"
     │
     ▼
1. Embed the question → vector Q
     │
     ▼
2. Search vector store → Top-10 closest chunk vectors
     │
     ▼
3. Return those chunks' file_path + character range
```

### Basic Retrieval Function

```python
def retrieve(question: str, k: int = 10) -> list[dict]:
    """
    Given a question, return top-k most relevant chunks.
    Each chunk has: file_path, first_character_index, last_character_index
    """
    # 1. Embed the question
    q_vec = model.encode([question]).astype("float32")
    faiss.normalize_L2(q_vec)
    
    # 2. Search
    distances, indices = index.search(q_vec, k)
    
    # 3. Format results
    results = []
    for idx in indices[0]:
        if idx == -1:  # FAISS returns -1 if fewer than k results
            break
        chunk = chunks[idx]
        results.append({
            "file_path": chunk["file_path"],
            "first_character_index": chunk["first_character_index"],
            "last_character_index": chunk["last_character_index"]
        })
    
    return results
```

### Advanced Retrieval Techniques

Once your basic retrieval works, you can improve with:

#### 🔁 Query Expansion
Before embedding the question, rewrite it or add keywords:
```python
def expand_query(question):
    # Add "Python code" or "vLLM" context
    return f"vLLM Python source code: {question}"
```

#### 🏷️ BM25 + Semantic Hybrid Search
Combine traditional keyword search (BM25) with semantic search for better results:
```python
from rank_bm25 import BM25Okapi

# Tokenize chunks
tokenized = [chunk["text"].split() for chunk in chunks]
bm25 = BM25Okapi(tokenized)

# Get BM25 scores
bm25_scores = bm25.get_scores(question.split())

# Combine with semantic scores (normalize both to 0-1 first)
combined_scores = 0.5 * semantic_scores + 0.5 * bm25_scores
```

#### 🔄 Reranking
After getting top-K results, use a cross-encoder to rerank them:
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
pairs = [(question, chunk["text"]) for chunk in top_chunks]
scores = reranker.predict(pairs)
# Sort chunks by reranker score
```

---

## 7. Step 5 — Evaluation: How Do You Know It Works?

### 📊 The Recall@K Metric

Your project uses **Recall@K** to measure quality.

> **Definition**: Recall@K = "Did the correct answer appear anywhere in my top K results?"

**Example:**
```
Ground truth: chunk from fused_batched_moe.py (chars 28416-28975)

Your top-10 results:
  Rank 1: some_other_file.py (chars 100-500)    ❌
  Rank 2: fused_batched_moe.py (chars 28416-28975) ✅ ← Found it at rank 2!
  Rank 3: ...
  ...

Recall@1 = 0  (not found in top-1)
Recall@2 = 1  (found in top-2)
Recall@3 = 1  (found in top-3)
Recall@5 = 1  (found in top-5)
```

**Overall Recall@K** = Average across all questions:
```
Recall@5 = (number of questions where correct answer is in top-5) / (total questions)
```

### Your Pass Thresholds

| Dataset | Metric | Threshold | What it means |
|---------|--------|-----------|---------------|
| **Code** | Recall@5 | ≥ 50% | For code questions, find the right chunk in top-5 at least half the time |
| **Docs** | Recall@5 | ≥ 80% | For docs questions, find the right chunk in top-5 at least 80% of the time |

> The Docs threshold is higher because documentation is usually more semantically clear than code.

### How the Moulinette Checks Your Answer

The evaluator uses **character overlap** — it checks if your returned character range overlaps with the ground truth range in the same file:
```
Ground truth: file.py, chars 28416–28975
Your result:  file.py, chars 28000–29000  ← ✅ Overlaps!
Your result:  other_file.py, chars 0–500  ← ❌ Wrong file
```

---

## 8. Your Dataset — What You're Working With

### 📂 Dataset Structure

```
datasets_public/public/
├── AnsweredQuestions/
│   ├── dataset_code_public.json   ← Code questions WITH correct answers
│   └── dataset_docs_public.json   ← Docs questions WITH correct answers
└── UnansweredQuestions/
    ├── dataset_code_public.json   ← Code questions WITHOUT answers (test set)
    └── dataset_docs_public.json   ← Docs questions WITHOUT answers (test set)
```

### 🏋️ Answered Questions = Your Training/Dev Set
Use these to **build and tune** your system. The `sources` field tells you exactly what the right answer is.

```json
{
  "question_id": "189c8b8a-...",
  "question": "What activation formats does the fused batched MoE layer return?",
  "answer": "The fused batched MoE layer returns a tuple of two mk.FusedMoEActivationFormat.BatchedExperts values...",
  "sources": [
    {
      "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
      "first_character_index": 28416,
      "last_character_index": 28975
    }
  ]
}
```

### 🧪 Unanswered Questions = Your Test Set
These are what you'll actually submit. No `sources` field — you need to find them!

### Two Types of Questions

| Type | Example | Strategy |
|------|---------|----------|
| **Code** | *"What is the default value of trust_remote_code in LLM class?"* | Search `.py` files |
| **Docs** | *"How do I configure tensor parallelism in vLLM?"* | Search `.md`, `.rst` docs files |

> 💡 **Tip**: You may want to build **two separate indexes** — one for code, one for docs — and route questions accordingly.

---

## 9. Your Evaluation System (the Moulinette)

The `README.md` in your project describes a CLI tool to evaluate your results.

### Running the Evaluator

```bash
uv run python -m moulinette evaluate_student_search_results \
    path/to/your/output/search_results.json \
    datasets_public/public/AnsweredQuestions/dataset_code_public.json \
    --k 10 \
    --max_context_length 2000
```

### Output Format You Must Produce

```json
{
  "search_results": [
    {
      "question_id": "189c8b8a-e59c-4fca-92ad-c02df42cbe40",
      "question": "What activation formats does the fused batched MoE layer return in vLLM?",
      "retrieved_sources": [
        {
          "file_path": "data/raw/vllm-0.10.1/vllm/model_executor/layers/fused_moe/fused_batched_moe.py",
          "first_character_index": 28416,
          "last_character_index": 28975
        },
        { ... },
        ...
      ]
    },
    ...
  ],
  "k": 10
}
```

> ⚠️ **Critical**: The `file_path` must exactly match the format in the dataset: `data/raw/vllm-0.10.1/...`

---

## 10. The Full Pipeline at a Glance

```
┌─────────────────────────────────────────────────────┐
│                 INDEXING PHASE (Run Once)            │
│                                                     │
│  vllm-0.10.1/                                       │
│  ├── vllm/*.py         ──► Chunker ──► Embedder     │
│  ├── docs/*.md         ──►         ──►              │
│  └── ...               ──►         ──►              │
│                                     │               │
│                              FAISS Index +           │
│                              chunks.json             │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  SEARCH PHASE (Per Question)        │
│                                                     │
│  Question ──► Embed ──► FAISS Search                │
│                              │                      │
│                         Top-10 chunks               │
│                              │                      │
│                     Format as JSON output           │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  EVALUATION PHASE                   │
│                                                     │
│  Your JSON ──► Moulinette ──► Recall@1/3/5/10       │
│                                                     │
│  Code:  Recall@5 >= 50%  → ✅ PASS                  │
│  Docs:  Recall@5 >= 80%  → ✅ PASS                  │
└─────────────────────────────────────────────────────┘
```

---

## 11. Key Tools & Libraries You'll Use

### Essential Libraries

```bash
uv add sentence-transformers   # Embedding models
uv add faiss-cpu               # Vector search (use faiss-gpu if you have GPU)
uv add rank-bm25               # BM25 keyword search
uv add tqdm                    # Progress bars
uv add numpy                   # Array operations
```

### Optional (for advanced techniques)

```bash
uv add transformers            # Hugging Face models
uv add torch                   # Required by transformers
uv add chromadb                # Alternative vector store
uv add langchain               # RAG framework (optional, can do manually)
```

### File Processing

```python
import os
import json
from pathlib import Path

# Walk the entire vllm directory
vllm_root = Path("vllm-0.10.1")
for file_path in vllm_root.rglob("*.py"):
    with open(file_path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Now chunk `content`
```

---

## 12. Common Pitfalls & How to Avoid Them

### ❌ Pitfall 1: Wrong File Paths
**Problem**: Your output uses `vllm-0.10.1/vllm/...` but the dataset expects `data/raw/vllm-0.10.1/vllm/...`

**Fix**: Always prefix your file paths correctly when building chunks:
```python
file_path = f"data/raw/{relative_path}"  # e.g., "data/raw/vllm-0.10.1/vllm/..."
```

### ❌ Pitfall 2: Chunks Too Large or Too Small
**Problem**: Chunks of 5000 chars dilute the signal; chunks of 50 chars lose context.

**Fix**: Use 300–800 character chunks with 50–150 char overlap for code.

### ❌ Pitfall 3: Not Handling Encoding Errors
**Problem**: Some files have non-UTF-8 characters and crash your reader.

**Fix**: Always use `errors="ignore"` when reading:
```python
with open(file_path, encoding="utf-8", errors="ignore") as f:
    content = f.read()
```

### ❌ Pitfall 4: Forgetting to Normalize Embeddings
**Problem**: Cosine similarity requires normalized vectors; FAISS's `IndexFlatIP` assumes they are.

**Fix**: Always call `faiss.normalize_L2(embeddings)` before adding to index and before searching.

### ❌ Pitfall 5: Re-embedding Everything on Every Run
**Problem**: Embedding 500,000 chunks takes time. Don't do it every time.

**Fix**: Save your index and chunk metadata to disk and reload:
```python
faiss.write_index(index, "index.faiss")
# Load later:
index = faiss.read_index("index.faiss")
```

### ❌ Pitfall 6: Ignoring the `max_context_length` parameter
**Problem**: The evaluator uses `--max_context_length 2000` by default, meaning only 2000 chars per source are used for context.

**Fix**: Keep your chunk sizes within reason (≤ 2000 chars).

---

## 13. Strategy to Beat the Thresholds

### 🥉 Level 1 — Baseline (Get ~40% Recall@5)
1. Chunk all `.py` files with fixed size (512 chars, overlap 64)
2. Embed with `all-MiniLM-L6-v2`
3. Store in FAISS
4. Search and output top-10

### 🥈 Level 2 — Solid (Get ~60-70% Recall@5)
1. Better embeddings: `BAAI/bge-base-en-v1.5`
2. Smarter chunking: function-level for Python
3. Add query prefix: `"Represent this code query: {question}"`
4. Separate index for code vs. docs

### 🥇 Level 3 — Advanced (Get 80%+ Recall@5)
1. **Hybrid search**: BM25 + semantic, combine scores
2. **Reranking**: Use a cross-encoder after top-50 retrieval
3. **Query expansion**: Use an LLM to rewrite the question
4. **Code-specific embedding model**: `nomic-ai/nomic-embed-code`
5. **Multiple chunk sizes**: Index chunks at 256, 512, and 1024 chars, search all

### 🏆 The Winning Strategy (Summary)

```
Questions → [Query Expansion] → Embed
                                    ↓
         BM25 Index ──────────► Merge & Rerank ──► Top 10
         FAISS Index ──────────►
```

---

## 🎯 Where to Start (Your First Steps)

1. **Read all `.py` files** from `vllm-0.10.1/`
2. **Chunk them** at 512 characters with 64-char overlap
3. **Save chunk metadata** (file_path, first_char, last_char, text) to a JSON file
4. **Embed all chunks** using `BAAI/bge-base-en-v1.5`
5. **Build a FAISS index** and save it to disk
6. **Loop over the answered questions**, call your retrieval function
7. **Format the output JSON** and run the moulinette evaluator
8. **Iterate**: look at which questions you got wrong and why

> 💬 **Remember**: The goal is Recall@5. You don't need the perfect answer at rank 1 — you just need it *somewhere* in your top 5. Start with a high-recall, low-precision approach and refine from there.

---

*Good luck with your project! You've got everything you need to crush those thresholds. 🚀*

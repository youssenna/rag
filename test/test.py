
import json
import re
from collections import Counter

import pytest

from src.index import MdFileChunker, PyFileChunker, Index


# ----------------------------------
# 1. Tokenization tests
# ----------------------------------

@pytest.mark.parametrize(
    "text, expected",
    [
        ("Hello World", ["hello", "world"]),
        ("Python 123", ["python", "123"]),
        ("RAG_Project", ["rag", "project"]),
        ("ABC abc", ["abc", "abc"]),
        ("", []),
        ("Hello, world! 2026.", ["hello", "world", "2026"]),
    ],
)
def test_tokenization(text, expected):
    result = MdFileChunker._tokonization(text)

    assert result == expected


# ----------------------------------
# 2. Repetition tests
# ----------------------------------

def test_tokens_repetition():
    chunker = MdFileChunker.__new__(MdFileChunker)

    tokens = ["python", "hello", "python", "world", "hello"]

    result = chunker._tokens_repetition(
        tokens.copy(),
        list(set(tokens))
    )

    assert result == {
        "python": 2,
        "hello": 2,
        "world": 1
    }


def test_tokens_repetition_empty():
    chunker = MdFileChunker.__new__(MdFileChunker)

    result = chunker._tokens_repetition([], [])

    assert result == {}


# ----------------------------------
# 3. Chunking tests
# ----------------------------------

@pytest.fixture(params=[MdFileChunker, PyFileChunker])
def chunker_class(request):
    return request.param


def create_chunker(tmp_path, chunker_class, content, max_size=20):
    file_path = tmp_path / "test_file.txt"

    file_path.write_text(content, encoding="utf-8")

    return chunker_class(str(file_path), max_size)


def test_empty_file(tmp_path, chunker_class):
    chunker = create_chunker(
        tmp_path,
        chunker_class,
        ""
    )

    chunks = chunker.get_chunks()

    assert chunks == []


def test_single_chunk(tmp_path, chunker_class):
    content = "Hello world!\n"

    chunker = create_chunker(
        tmp_path,
        chunker_class,
        content,
        max_size=100
    )

    chunks = chunker.get_chunks()

    assert len(chunks) == 1
    assert chunks[0].text_content == content


def test_multiple_chunks(tmp_path, chunker_class):
    content = (
        "First line\n"
        "Second line\n"
        "Third line\n"
        "Fourth line\n"
    )

    chunker = create_chunker(
        tmp_path,
        chunker_class,
        content,
        max_size=20
    )

    chunks = chunker.get_chunks()

    assert len(chunks) > 1

    # No content should be lost or duplicated.
    reconstructed = "".join(
        chunk.text_content for chunk in chunks
    )

    assert reconstructed == content


def test_long_line_splitting(tmp_path, chunker_class):
    content = "abcdefghijklmnopqrstuvwxyz"

    chunker = create_chunker(
        tmp_path,
        chunker_class,
        content,
        max_size=10
    )

    chunks = chunker.get_chunks()

    assert len(chunks) == 3

    reconstructed = "".join(
        chunk.text_content for chunk in chunks
    )

    assert reconstructed == content

    assert all(
        len(chunk.text_content) <= 10
        for chunk in chunks
    )


# ----------------------------------
# 4. Character indexes tests
# ----------------------------------

def test_character_indexes(tmp_path, chunker_class):
    # The second line is deliberately longer
    # than max_chunk_size.
    content = (
        "abc def\n"
        "0123456789ABCDEFGHIJKLM\n"
    )

    chunker = create_chunker(
        tmp_path,
        chunker_class,
        content,
        max_size=10
    )

    chunks = chunker.get_chunks()

    for chunk in chunks:
        start = chunk.first_character_index
        end = chunk.last_character_index

        assert chunk.text_content == content[start:end + 1]

    reconstructed = "".join(
        chunk.text_content for chunk in chunks
    )

    assert reconstructed == content


# ----------------------------------
# 5. Metadata tests
# ----------------------------------

def test_chunk_metadata(tmp_path, chunker_class):
    content = "Python python RAG project python"

    chunker = create_chunker(
        tmp_path,
        chunker_class,
        content,
        max_size=100
    )

    chunks = chunker.get_chunks()

    assert len(chunks) == 1

    chunk = chunks[0]

    expected_tokens = re.findall(
        r"[\da-zA-Z]+",
        content.lower()
    )

    expected_repetition = dict(
        Counter(expected_tokens)
    )

    assert chunk.tokens_len == len(expected_tokens)
    assert chunk.repetition == expected_repetition
    assert chunk.file_path == str(tmp_path / "test_file.txt")


# ----------------------------------
# 6. Index integration test
# ----------------------------------

def test_index_run(tmp_path, monkeypatch):
    # Create the directory structure expected by Index.
    root = tmp_path / "data" / "raw" / "vllm-0.10.1"
    root.mkdir(parents=True)

    (root / "example.py").write_text(
        "def hello():\n    return 'world'\n",
        encoding="utf-8"
    )

    (root / "README.md").write_text(
        "# Example\nThis is a test.\n",
        encoding="utf-8"
    )

    # Make relative paths resolve inside tmp_path.
    monkeypatch.chdir(tmp_path)

    index = Index(max_chunk_size=100)

    index.run()

    saved_file = (
        tmp_path / "data" / "processed" / "chunks.json"
    )

    assert saved_file.exists()

    with saved_file.open(encoding="utf-8") as f:
        saved_chunks = json.load(f)

    assert len(saved_chunks) > 0

    # Both Python and Markdown files should be indexed.
    indexed_files = {
        chunk["file_path"] for chunk in saved_chunks
    }

    assert str(root / "example.py") in indexed_files
    assert str(root / "README.md") in indexed_files

    # Check that saved chunks contain their metadata.
    for chunk in saved_chunks:
        assert "tokens_len" in chunk
        assert "repetition" in chunk
        assert chunk["tokens_len"] >= 0

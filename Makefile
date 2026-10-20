PYTHON =uv run python3
MYPY = uv run mypy
FLAKE8 = uv run flake8

install:
        uv sync


run: install
        clear
        $(PYTHON) -m main.py

debug: install
        clear
        $(PYTHON) -m pdb main.py

clean:
        find . \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".venv" -o -name "venv" -o -name "cache" \) -exec rm -rf {} +

lint:
        FLAKE8 .
        MYPY  . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs


lint-strict:
        FLAKE8 .
        MYPY . --strict%  
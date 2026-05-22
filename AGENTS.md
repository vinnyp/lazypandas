# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

**lazypandas** — a small Python library of helper methods that wrap common pandas data-wrangling chores (timestamped CSV exports, simple CSV imports, missing-value examination). Originally written in 2018; currently being modernized.

Public API (re-exported from `src/lazypandas/__init__.py`):

- `lazypandas.import_df(file_name, *args, **kwargs)` — load a CSV from `path_in` by substring match on filename. Raises `ValueError` on ambiguous matches.
- `lazypandas.export_df(df, label='', show_index=False, trace=True, *args, **kwargs)` — write a DataFrame to `path_out` with a session-shared timestamp prefix. `trace=True` appends a version counter; `trace=False` overwrites.
- Module-level config: `lazypandas.path_in`, `lazypandas.path_out`, `lazypandas.timestamp_label`.

## Layout

```
lazypandas/
├── src/lazypandas/
│   ├── __init__.py        # Public surface + module-level wrappers
│   └── io.py              # Export & Import classes
├── tests/
│   ├── conftest.py        # Session-scope test isolation
│   ├── test_bugs.py       # Regression tests for B1-B6
│   ├── test_export_df.py
│   ├── test_import_df.py
│   └── file_output/       # Test artifact dir (gitignored)
├── docs/superpowers/      # Spec + plan for the modernization effort
├── pyproject.toml         # PEP 621 packaging metadata
├── README.md
├── CHANGELOG.md
└── LICENSE
```

## Dev environment

Python is managed by **`uv`**. The project venv lives at `.venv/` and is created with Python 3.11.

```bash
# One-time setup
uv venv --python 3.11 .venv
uv pip install -e ".[dev]"   # installs pytest, pytest-cov

# Run tests
.venv/bin/pytest -v

# Add a dep
uv pip install <package>
```

Declared deps: `pandas>=2.2`, `numpy>=1.26`. Requires Python `>=3.10`.

## Conventions & guardrails

**Pre-approved (no confirmation needed):**
- Local file edits, reads, writes within this repo.
- Bash commands for build/test/lint/install (use `uv`, not bare `pip`).
- Creating, modifying, deleting files in the working tree.
- Local git operations: `add`, `commit`, `branch`, `checkout`, `status`, `diff`, `log`.

**Always confirm with the user first:**
- `git push` (any branch).
- Opening, merging, or closing PRs (`gh pr create`, `gh pr merge`, `gh pr close`).
- Creating, editing, or closing GitHub issues (`gh issue ...`).
- Creating or modifying labels.
- Any destructive operation: `git reset --hard`, `git push --force`, `rm -rf`, deleting branches.
- Modifying GitHub Actions workflows or repo settings.
- Releases, tags published to remote.

**Style:**
- Use `uv` for Python env/dep management.
- Prefer `pathlib.Path` over string-concatenated paths.
- Prefer pytest fixtures (`tmp_path`, `caplog`) over manual setup in tests.
- Use `logging`, not `print`, in library code.
- Conventional Commits (`fix:`, `feat:`, `chore:`, `refactor:`, `docs:`, `test:`, `build:`, `ci:`).

# AGENTS.md

Guidance for AI coding agents working in this repository.

## Project overview

**lazypandas** — a small Python library of helper methods that wrap common pandas data-wrangling chores (timestamped CSV exports, simple CSV imports). Originally written in 2018; currently being modernized.

Public API (re-exported from `lazypandas/__init__.py`):

- `lazypandas.import_df(file_name, *args, **kwargs)` — load a CSV from `path_in` by substring match on filename.
- `lazypandas.export_df(df, label='', show_index=False, trace=True, *args, **kwargs)` — write a DataFrame to `path_out` with a session-shared timestamp prefix. `trace=True` appends a version counter; `trace=False` overwrites.
- Module-level config: `lazypandas.path_in`, `lazypandas.path_out`, `lazypandas.timestamp_label`.

## Layout

```
lazypandas/
├── lazypandas/
│   ├── __init__.py        # Public surface + module-level wrappers
│   └── io.py              # Export & Import classes (singletons)
├── tests/
│   ├── test_export_df.py
│   ├── test_import_df.py
│   └── file_output/       # Test artifact dir (gitignored *.csv)
├── setup.py               # Legacy packaging (modernization target)
├── tox.ini                # py36 only (modernization target)
├── README.rst             # Stub (modernization target)
└── LICENSE
```

## Dev environment

Python is managed by **`uv`**. The project venv lives at `.venv/` and is created with Python 3.11.

```bash
# One-time setup
uv venv --python 3.11 .venv
uv pip install -e . pytest

# Run tests
.venv/bin/pytest tests/ -v

# Add a dep
uv pip install <package>
```

Current pinned deps (from `setup.py`, intentionally outdated):
`pandas>=0.23.1`, `numpy>=1.14.3`. Modern versions (pandas 3.x, numpy 2.x) work — code is mostly compatible.

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

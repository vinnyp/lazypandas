# lazypandas Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize and revive the 2018-era `lazypandas` library: fix latent bugs, migrate to modern Python packaging, clean up tests, add CI, and improve code style — while preserving the public API.

**Architecture:** Six chunks executed in two waves. Wave 1 (bugs / packaging / readme) runs in parallel worktrees; wave 2 (tests / CI / polish) follows after wave 1 lands. Each chunk lives on its own `chunk/<name>` branch, gets reviewed via `superpowers:requesting-code-review` (alternating Claude / codex), and merges via conventional-commit squash PR.

**Tech Stack:** Python 3.10+, pandas 2.x/3.x, numpy 2.x, `uv` for env/deps, `pytest` for tests, `pyproject.toml` (PEP 621) for packaging, `ruff` for lint/format, GitHub Actions for CI.

**Reference:** Spec at `docs/superpowers/specs/2026-05-22-lazypandas-modernization-design.md` — bug/finding IDs (B1–B6, D1–D8, T1–T7, P1–P9, H1–H5) reference that doc.

---

## Per-chunk workflow (applies to every chunk)

Each chunk follows this loop:

1. `git worktree add ../lazypandas-<chunk> -b chunk/<name>` from `master`.
2. In the worktree: `uv venv --python 3.11 .venv && uv pip install -e . pytest` (so it has a working env).
3. Execute the chunk's tasks below (strict TDD on bug fixes — write failing test first, then fix).
4. Run `.venv/bin/pytest -v` — all green.
5. Invoke `superpowers:requesting-code-review`. **Reviewer alternation:**
   - chunk-bugs → Claude implements, codex reviews
   - chunk-pkg → codex implements, Claude reviews
   - chunk-readme → Claude implements, codex reviews
   - chunk-tests → codex implements, Claude reviews
   - chunk-ci → Claude implements, codex reviews
   - chunk-polish → codex implements, Claude reviews
6. Address review comments; re-verify.
7. **CONFIRM WITH USER** before pushing.
8. `git push -u origin chunk/<name>`, `gh pr create --title "<conventional commit>" --body "..."`, `gh pr merge --squash`.
9. `git worktree remove ../lazypandas-<chunk>`.

---

# WAVE 1 — parallel: bugs, packaging, readme

## Chunk-bugs: fix the latent bugs (TDD)

**Branch:** `chunk/bugs`
**Files:**
- Modify: `lazypandas/io.py`
- Create: `tests/test_bugs.py` (regression tests for B1–B6)

**Notes:**
- Use existing `tests/file_output/` as `path_in/path_out` to stay consistent with existing tests, OR (preferred) use `tmp_path` from pytest for full isolation. This plan uses `tmp_path` for new tests.
- B5 (session-shared timestamp) is **deferred** to chunk-polish; document only here, don't change behavior.

### Task 1: B2 — fix masked IndexError in `import_df`

**Files:**
- Modify: `lazypandas/io.py:132`
- Create test in: `tests/test_bugs.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_bugs.py
import pandas as pd
import numpy as np
import pytest
import lazypandas as lp


def _sample_df():
    return pd.DataFrame(np.random.randn(5, 2), columns=["A", "B"])


def test_b2_import_df_missing_file_raises_indexerror(tmp_path):
    """B2: logger.exception was wrapping IndexError into TypeError."""
    # Seed the import dir with one unrelated csv so the directory is not empty
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    lp.export_df(_sample_df(), label="seed", trace=False)

    with pytest.raises(IndexError):
        lp.import_df("not_a_real_file.csv")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b2_import_df_missing_file_raises_indexerror -v
```
Expected: FAIL — currently raises `TypeError` ("not all arguments converted during string formatting").

- [ ] **Step 3: Fix the bug**

In `lazypandas/io.py`, change line ~132 from:
```python
self.logger.exception('No file found with that name.', e)
```
to:
```python
self.logger.exception('No file found with that name.')
```
(`logger.exception()` already captures the active traceback.)

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b2_import_df_missing_file_raises_indexerror -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add lazypandas/io.py tests/test_bugs.py
git commit -m "fix(io): propagate IndexError from import_df instead of masking with TypeError (B2)"
```

### Task 2: B3 — fix broken `logger.exception` in `export_df`

**Files:**
- Modify: `lazypandas/io.py:74,81`
- Add test to: `tests/test_bugs.py`

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/test_bugs.py
def test_b3_export_df_handles_exception_correctly(tmp_path, monkeypatch):
    """B3: logger.exception(self, ...) crashes when the export path is unwritable."""
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)

    # Force pandas.to_csv to raise so the except branch is exercised
    import pandas as pd
    def boom(*args, **kwargs):
        raise OSError("disk on fire")
    monkeypatch.setattr(pd.DataFrame, "to_csv", boom)

    # Today this raises TypeError from the broken logger.exception(self, ...) call,
    # masking the IOError("Exported file not found.") that the function intends.
    with pytest.raises((OSError, IOError)):
        lp.export_df(_sample_df(), label="boomtest", trace=False)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b3_export_df_handles_exception_correctly -v
```
Expected: FAIL — `TypeError` from the broken `logger.exception(self, "Exception: ", e)` call.

- [ ] **Step 3: Fix the bug**

In `lazypandas/io.py`, replace both `self.logger.exception(self, "Exception: ", e)` calls (one in the `trace` branch, one in the `not trace` branch) with:
```python
self.logger.exception("Error writing CSV")
raise
```
The `raise` re-raises the original exception so callers see real errors.

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b3_export_df_handles_exception_correctly -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add lazypandas/io.py tests/test_bugs.py
git commit -m "fix(io): correct logger.exception signature in export_df and re-raise (B3)"
```

### Task 3: B1 — fix `len(file)` → `len(df)` in import_df log line

**Files:**
- Modify: `lazypandas/io.py:130`
- Add test to: `tests/test_bugs.py`

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/test_bugs.py
def test_b1_import_df_logs_correct_row_count(tmp_path, caplog):
    """B1: import_df logs len(file) (filename length) instead of len(df)."""
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    df = _sample_df()  # 5 rows
    lp.export_df(df, label="rows_check", trace=False)

    import logging
    with caplog.at_level(logging.INFO, logger="lazypandas.io"):
        lp.import_df("rows_check.csv")

    # Must log "Total rows: 5", not the length of the file path string.
    assert any("Total rows: 5" in rec.getMessage() for rec in caplog.records)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b1_import_df_logs_correct_row_count -v
```
Expected: FAIL — log will contain a path-length integer like "Total rows: 47".

- [ ] **Step 3: Fix the bug**

In `lazypandas/io.py`, change:
```python
self.logger.info("Total rows: " + str(len(file)))
```
to:
```python
self.logger.info("Total rows: %d", len(df))
```

- [ ] **Step 4: Run test to verify it passes**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b1_import_df_logs_correct_row_count -v
```
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add lazypandas/io.py tests/test_bugs.py
git commit -m "fix(io): log dataframe row count, not filename length, in import_df (B1)"
```

### Task 4: B4 — use `pathlib` for output paths

**Files:**
- Modify: `lazypandas/io.py:71,78` (and `_file_exists` if needed)
- Add test to: `tests/test_bugs.py`

- [ ] **Step 1: Write the failing test**

```python
# Append to tests/test_bugs.py
def test_b4_export_df_works_without_trailing_slash(tmp_path):
    """B4: string-concatenated paths break when path_out lacks a trailing slash."""
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    # Set path_out WITHOUT a trailing slash on purpose.
    lp.path_out = str(out_dir)
    lp.path_in = str(out_dir)

    lp.export_df(_sample_df(), label="noslash", trace=False)

    # File must land inside out_dir, not at out_dir's parent with a concat'd name.
    found = list(out_dir.glob("*noslash*.csv"))
    assert len(found) == 1, f"Expected exactly one csv inside {out_dir}, found {found}"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b4_export_df_works_without_trailing_slash -v
```
Expected: FAIL — file written one directory up or with malformed name.

- [ ] **Step 3: Fix the bug**

In `lazypandas/io.py`, replace both path construction lines:
```python
# Before:
buffer = self.path_out + self.timestamp_label + label + str(file_count + 1) + '.csv'
# ...
buffer = self.path_out + self.timestamp_label + label + '.csv'
```
With:
```python
from pathlib import Path  # already imported at top, ensure present
# Trace branch:
buffer = str(Path(self.path_out) / f"{self.timestamp_label}{label}{file_count + 1}.csv")
# Non-trace branch:
buffer = str(Path(self.path_out) / f"{self.timestamp_label}{label}.csv")
```

Also update the glob in `export_df`:
```python
all_files = glob.glob(str(Path(self.path_out) / f"{self.timestamp_label}{label}*.csv"))
```

- [ ] **Step 4: Run test to verify it passes + no regressions**

```bash
.venv/bin/pytest -v
```
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add lazypandas/io.py tests/test_bugs.py
git commit -m "fix(io): use pathlib for output path construction (B4)"
```

### Task 5: B6 — require exact filename match (or raise on ambiguity)

**Files:**
- Modify: `lazypandas/io.py:127`
- Add test to: `tests/test_bugs.py`

**Design decision:** Keep substring matching for backward compat, but **raise on ambiguity** (more than one match). This preserves existing test_file_imported behavior (which passes "accounts.csv" and gets the only file matching).

- [ ] **Step 1: Write the failing tests**

```python
# Append to tests/test_bugs.py
def test_b6_import_df_raises_on_ambiguous_match(tmp_path):
    """B6: silently popping last of multiple matches is dangerous."""
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    df = _sample_df()
    lp.export_df(df, label="report_v1", trace=False)
    lp.export_df(df, label="report_v2", trace=False)

    with pytest.raises(ValueError, match="ambiguous"):
        lp.import_df("report")  # matches both


def test_b6_import_df_single_match_still_works(tmp_path):
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    lp.export_df(_sample_df(), label="unique_label", trace=False)
    df = lp.import_df("unique_label.csv")
    assert len(df) == 5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
.venv/bin/pytest tests/test_bugs.py::test_b6_import_df_raises_on_ambiguous_match -v
```
Expected: FAIL — currently no ValueError raised.

- [ ] **Step 3: Fix the bug**

In `lazypandas/io.py`, replace:
```python
file = [y for y in all_files if file_name in y].pop()
```
with:
```python
matches = [y for y in all_files if file_name in y]
if not matches:
    raise IndexError(f"No file matching {file_name!r} in {self.path_in}")
if len(matches) > 1:
    raise ValueError(
        f"ambiguous match for {file_name!r}: found {len(matches)} files: {matches}"
    )
file = matches[0]
```

- [ ] **Step 4: Run tests + full suite**

```bash
.venv/bin/pytest -v
```
Expected: all PASS, including pre-existing tests.

- [ ] **Step 5: Commit**

```bash
git add lazypandas/io.py tests/test_bugs.py
git commit -m "fix(io): raise ValueError on ambiguous import_df matches (B6)"
```

### Task 6: chunk-bugs final review

- [ ] **Step 1:** Run full suite: `.venv/bin/pytest -v` — expect all green.
- [ ] **Step 2:** Invoke `superpowers:requesting-code-review` against `chunk/bugs`. Reviewer: **codex** (`codex exec --cd <path> "review the diff against master..."`).
- [ ] **Step 3:** Address review comments, re-run tests.
- [ ] **Step 4:** Confirm with user → push → open PR `fix: address latent bugs B1-B4, B6` → squash-merge.

---

## Chunk-pkg: migrate to pyproject.toml + src layout

**Branch:** `chunk/pkg`
**Files:**
- Create: `pyproject.toml`
- Create: `src/lazypandas/__init__.py` (moved from `lazypandas/__init__.py`)
- Create: `src/lazypandas/io.py` (moved from `lazypandas/io.py`)
- Delete: `lazypandas/` (top-level package dir)
- Delete: `setup.py`
- Delete: `tox.ini`

### Task 1: Move package to `src/` layout

- [ ] **Step 1: Move files**

```bash
mkdir -p src
git mv lazypandas src/lazypandas
```

- [ ] **Step 2: Verify nothing else references the old path**

```bash
git grep -n "lazypandas/io.py\|lazypandas/__init__.py" -- ':!*.md' ':!docs/'
```
Expected: no hits in source files.

### Task 2: Create `pyproject.toml`

- [ ] **Step 1: Write the file**

```toml
# pyproject.toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "lazypandas"
version = "0.2.0"
description = "A collection of data wrangling helper methods for pandas."
readme = "README.md"
license = { file = "LICENSE" }
authors = [{ name = "Vinny Pasceri", email = "vinnypasceri@gmail.com" }]
requires-python = ">=3.10"
keywords = ["pandas", "dataframe", "csv", "helpers"]
classifiers = [
  "Development Status :: 3 - Alpha",
  "Framework :: Jupyter",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.10",
  "Programming Language :: Python :: 3.11",
  "Programming Language :: Python :: 3.12",
  "Programming Language :: Python :: 3.13",
]
dependencies = [
  "pandas>=2.2",
  "numpy>=1.26",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5"]

[project.urls]
Homepage = "https://github.com/vinnyp/lazypandas"
Repository = "https://github.com/vinnyp/lazypandas"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra"
```

- [ ] **Step 2: Delete `setup.py` and `tox.ini`**

```bash
git rm setup.py tox.ini
```

### Task 3: Verify install + tests still work

- [ ] **Step 1: Re-create venv from scratch**

```bash
rm -rf .venv
uv venv --python 3.11 .venv
uv pip install -e ".[dev]"
```
Expected: install succeeds.

- [ ] **Step 2: Run full test suite**

```bash
.venv/bin/pytest -v
```
Expected: all PASS.

- [ ] **Step 3: Verify import path**

```bash
.venv/bin/python -c "import lazypandas; print(lazypandas.__file__)"
```
Expected: prints a path under `src/lazypandas/__init__.py`.

### Task 4: Commit + chunk-pkg final review

- [ ] **Step 1: Commit**

```bash
git add pyproject.toml src/
git rm setup.py tox.ini  # if not already
git commit -m "build: migrate to pyproject.toml and src/ layout (P1, P3, P4, P9)

- Add PEP 621 metadata in pyproject.toml.
- Bump declared deps to pandas>=2.2, numpy>=1.26 (P2).
- requires-python = '>=3.10' (P3).
- Delete setup.py and tox.ini.
- Move lazypandas/ -> src/lazypandas/ (P9)."
```

- [ ] **Step 2:** Invoke `superpowers:requesting-code-review`. Reviewer: **Claude**.
- [ ] **Step 3:** Address review, re-run tests.
- [ ] **Step 4:** Confirm with user → push → PR `build: migrate to pyproject.toml and src layout` → squash-merge.

---

## Chunk-readme: docs + changelog + gitignore

**Branch:** `chunk/readme`
**Files:**
- Create: `README.md`
- Delete: `README.rst`
- Create: `CHANGELOG.md`
- Modify: `.gitignore` (scope `*.csv`)

### Task 1: Write README.md

- [ ] **Step 1: Create README.md**

```markdown
# lazypandas

A small collection of data-wrangling helper methods for pandas — currently focused on timestamped CSV import/export.

## Installation

```bash
uv pip install lazypandas
# or
pip install lazypandas
```

## Quick start

```python
import lazypandas as lp
import pandas as pd

df = pd.DataFrame({"a": [1, 2, 3]})

lp.path_out = "./exports/"
lp.export_df(df, label="snapshot")              # trace=True (default): versioned filenames
lp.export_df(df, label="snapshot", trace=False) # overwrite single file

lp.path_in = "./exports/"
df_loaded = lp.import_df("snapshot")            # substring match
```

## Features

- **`export_df(df, label, show_index, trace)`** — write a DataFrame to `path_out` with a session-shared timestamp prefix. `trace=True` appends a version counter; `trace=False` overwrites a single file.
- **`import_df(file_name)`** — load a CSV from `path_in` by substring match. Raises `ValueError` if more than one file matches.

## Configuration

| Name | Default | Purpose |
|---|---|---|
| `lazypandas.path_in` | `'./'` | Directory `import_df` reads from. |
| `lazypandas.path_out` | `'./'` | Directory `export_df` writes to. |
| `lazypandas.timestamp_label` | computed at import time | Prefix applied to all exports in a session. |

## Requirements

- Python ≥ 3.10
- pandas ≥ 2.2
- numpy ≥ 1.26

## License

MIT — see `LICENSE`.

## Authors

[Vinny Pasceri](mailto:vinnypasceri@gmail.com).
```

- [ ] **Step 2: Delete README.rst**

```bash
git rm README.rst
```

### Task 2: Create CHANGELOG.md

- [ ] **Step 1: Write the file**

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modern packaging via `pyproject.toml` (PEP 621).
- `src/` layout.
- GitHub Actions CI matrix.
- Type hints throughout the public API.
- Regression tests for bugs B1, B2, B3, B4, B6.

### Changed
- `import_df` now raises `ValueError` on ambiguous substring matches (was: silently picked one).
- `export_df` paths now built via `pathlib` (was: string concatenation, broke without trailing slash).
- `logger.exception` calls fixed to propagate real exceptions instead of `TypeError`.

### Removed
- `setup.py`, `tox.ini`, `README.rst`.

## [0.1.0] — 2018-06-30

- Initial release.
```

### Task 3: Scope `.gitignore` `*.csv` rule

- [ ] **Step 1: Modify `.gitignore`**

Replace the line `*.csv` near the bottom (under "# file export") with:
```
# file export — only ignore CSVs produced by tests, not all CSVs project-wide
tests/file_output/*.csv
```

### Task 4: Commit + chunk-readme review

- [ ] **Step 1: Commit**

```bash
git add README.md CHANGELOG.md .gitignore
git rm README.rst
git commit -m "docs: rewrite README as Markdown, add CHANGELOG, scope gitignore csv rule (H1, H2, H4)"
```

- [ ] **Step 2:** Invoke `superpowers:requesting-code-review`. Reviewer: **codex**.
- [ ] **Step 3:** Address review.
- [ ] **Step 4:** Confirm → push → PR `docs: rewrite README and add CHANGELOG` → squash-merge.

---

# WAVE 2 — sequential after wave 1 merges

After all three wave-1 PRs land on `master`, `git pull` master into each new worktree.

## Chunk-tests: pytest cleanup

**Branch:** `chunk/tests`
**Files:**
- Modify: `tests/test_export_df.py`
- Modify: `tests/test_import_df.py`
- Modify: `pyproject.toml` (add `pytest-cov` config)
- Delete: `tests/__init__.py` (if empty)
- Modify: `tests/file_output/` — remove or keep as `.keep` file

### Task 1: T1 — rename misnamed test class

- [ ] **Step 1: Modify `tests/test_import_df.py:10`**

Change `class TestExportDf(unittest.TestCase):` to `class TestImportDf(unittest.TestCase):`.

- [ ] **Step 2: Run tests**: `.venv/bin/pytest tests/test_import_df.py -v` — PASS.

### Task 2: T2 + T3 — convert to pytest functions, drop logger boilerplate

**Files:** rewrite both `tests/test_export_df.py` and `tests/test_import_df.py`.

- [ ] **Step 1: Rewrite `tests/test_export_df.py`**

```python
# tests/test_export_df.py
import glob
import os
import pandas as pd
import numpy as np
import pytest
from pathlib import Path

import lazypandas as lp


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        np.random.randn(10, 3),
        columns=["A", "B", "C"],
        index=pd.date_range("1/1/2000", periods=10),
    )


@pytest.fixture
def io_dir(tmp_path):
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    return tmp_path


def test_typeerror_input_df():
    with pytest.raises(TypeError):
        lp.export_df("not a dataframe")


def test_typeerror_input_label(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, label=1, trace=False)


def test_typeerror_input_index(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, show_index="yes")


def test_typeerror_input_trace(sample_df, io_dir):
    with pytest.raises(TypeError):
        lp.export_df(sample_df, label="df_account", trace="yes")


def test_final_exported(sample_df, io_dir):
    label = "random_numbers"
    lp.export_df(sample_df, label=label, trace=False)
    expected = io_dir / f"{lp.timestamp_label}{label}.csv"
    assert expected.is_file()


def test_trace_exported(sample_df, io_dir):
    for _ in range(4):
        lp.export_df(sample_df)
    all_files = glob.glob(str(io_dir / f"{lp.timestamp_label}iteration_*.csv"))
    assert len(all_files) == 4


def test_invalid_path():
    with pytest.raises((ValueError, NotADirectoryError, TypeError)):
        lp.path_out = "not_a_valid_path"
```

- [ ] **Step 2: Rewrite `tests/test_import_df.py`**

```python
# tests/test_import_df.py
import pandas as pd
import numpy as np
import pytest

import lazypandas as lp


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        np.random.randn(10, 3),
        columns=["A", "B", "C"],
        index=pd.date_range("1/1/2000", periods=10),
    )


@pytest.fixture
def io_dir(tmp_path):
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)
    return tmp_path


def test_file_not_found(io_dir, sample_df):
    lp.export_df(sample_df, label="seed", trace=False)
    with pytest.raises(IndexError):
        lp.import_df("users.csv")


def test_file_imported(sample_df, io_dir):
    lp.export_df(sample_df, label="accounts", trace=False)
    df = lp.import_df("accounts.csv")
    assert len(df) == 10


def test_invalid_path():
    with pytest.raises((ValueError, NotADirectoryError, TypeError)):
        lp.path_in = "not_a_valid_path"
```

- [ ] **Step 3: Run full suite**: `.venv/bin/pytest -v` — all PASS.

### Task 3: T4 — already done via `tmp_path` in tasks above

- [ ] **Step 1:** Verify no test writes into `tests/file_output/` anymore:

```bash
git grep -n "tests/file_output" tests/
```
Expected: no hits.

- [ ] **Step 2:** Remove the test-output dir if empty, or convert to `.keep`:

```bash
rm -rf tests/file_output
git add -u tests/file_output 2>/dev/null || true
```

### Task 4: T5 — content assertions

- [ ] **Step 1: Add to `tests/test_import_df.py`**

```python
def test_file_imported_contents_match(sample_df, io_dir):
    """T5: round-trip assertion using assert_frame_equal."""
    from pandas.testing import assert_frame_equal
    lp.export_df(sample_df, label="roundtrip", trace=False, show_index=True)
    df = lp.import_df("roundtrip.csv")
    # to_csv -> read_csv loses the DatetimeIndex name and column dtypes by default;
    # compare values only.
    assert_frame_equal(
        df.iloc[:, 1:].reset_index(drop=True),
        sample_df.reset_index(drop=True),
        check_dtype=False,
    )
```

- [ ] **Step 2:** Run: `.venv/bin/pytest tests/test_import_df.py::test_file_imported_contents_match -v` — PASS.

### Task 5: T6 — multi-match test (already in chunk-bugs as test_b6_*); confirm still present

- [ ] **Step 1:** Verify regression test from chunk-bugs is intact:

```bash
git grep -n "test_b6_import_df_raises_on_ambiguous_match" tests/
```
Expected: one hit in `tests/test_bugs.py`.

### Task 6: T7 — add coverage tooling

- [ ] **Step 1: Add to `pyproject.toml` `[tool.pytest.ini_options]`**

```toml
addopts = "-ra --cov=lazypandas --cov-report=term-missing"
```

- [ ] **Step 2: Add coverage threshold under a new `[tool.coverage.report]` section**

```toml
[tool.coverage.report]
fail_under = 80
show_missing = true
```

- [ ] **Step 3:** Run: `.venv/bin/pytest` — verify coverage table prints and threshold passes.

### Task 7: H3 — delete empty `tests/__init__.py`

- [ ] **Step 1:** `git rm tests/__init__.py`
- [ ] **Step 2:** Run: `.venv/bin/pytest -v` — still discovers tests.

### Task 8: Commit + chunk-tests review

- [ ] **Step 1: Commit**

```bash
git add tests/ pyproject.toml
git commit -m "test: convert to pytest functions, use tmp_path, add coverage (T1-T7, H3)"
```

- [ ] **Step 2:** Invoke `superpowers:requesting-code-review`. Reviewer: **Claude**.
- [ ] **Step 3:** Address review.
- [ ] **Step 4:** Confirm → push → PR `test: modernize test suite with fixtures and coverage` → squash-merge.

---

## Chunk-ci: GitHub Actions workflow

**Branch:** `chunk/ci`
**Files:**
- Create: `.github/workflows/ci.yml`

### Task 1: Write the workflow

- [ ] **Step 1: Create directory + file**

```bash
mkdir -p .github/workflows
```

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12", "3.13"]
        pandas-version: ["2.2.*", "3.0.*"]
        exclude:
          # pandas 2.2 wheels don't ship for 3.13 yet
          - python-version: "3.13"
            pandas-version: "2.2.*"
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          enable-cache: true

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Create venv & install
        run: |
          uv venv --python ${{ matrix.python-version }} .venv
          uv pip install --python .venv/bin/python -e ".[dev]"
          uv pip install --python .venv/bin/python "pandas==${{ matrix.pandas-version }}"

      - name: Run tests
        run: .venv/bin/pytest -v
```

- [ ] **Step 2: Verify locally that nothing's broken** (workflow itself only runs on GitHub):

```bash
.venv/bin/pytest -v
```
Expected: PASS.

### Task 2: Commit + chunk-ci review

- [ ] **Step 1: Commit**

```bash
git add .github/
git commit -m "ci: add GitHub Actions matrix (py 3.10-3.13 x pandas 2.x/3.x) (P7)"
```

- [ ] **Step 2:** Invoke `superpowers:requesting-code-review`. Reviewer: **codex**.
- [ ] **Step 3:** Address review.
- [ ] **Step 4:** Confirm → push → PR `ci: add GitHub Actions matrix` → squash-merge. **Verify workflow runs successfully on the PR before merging.**

---

## Chunk-polish: design cleanups, type hints, tooling

**Branch:** `chunk/polish`
**Files:**
- Modify: `src/lazypandas/io.py` (D1, D3, D4, D5, D6, D7)
- Modify: `src/lazypandas/__init__.py` (D2, D6, D8, H5)
- Modify: `pyproject.toml` (P5, P6)
- Create: `.pre-commit-config.yaml` (P8)
- Create: `ruff.toml` config inside `pyproject.toml`

### Task 1: D5 — fix path-setter exception type

- [ ] **Step 1: Add test in `tests/test_export_df.py` and `tests/test_import_df.py`**

```python
def test_invalid_path_raises_specific_error():
    with pytest.raises(NotADirectoryError):
        lp.path_out = "not_a_valid_path"
```
(Replaces the prior `test_invalid_path` which accepted multiple error types.)

- [ ] **Step 2: Modify both setters in `src/lazypandas/io.py`**

```python
@path_out.setter
def path_out(self, value):
    path = Path(value)
    if not path.is_dir():
        raise NotADirectoryError(f"Not a valid directory: {value!r}")
    self._path_out = value
```
(And the same for `Import.path_in`.)

- [ ] **Step 3:** Run: `.venv/bin/pytest -v` — PASS.

- [ ] **Step 4: Commit**: `git commit -am "refactor(io): raise NotADirectoryError for invalid paths (D5)"`

### Task 2: D4 — replace `print` with logging

- [ ] **Step 1: Modify `src/lazypandas/io.py:89`**

Change:
```python
print('Exported: ' + buffer)
```
to:
```python
self.logger.info("Exported: %s", buffer)
```

- [ ] **Step 2: Add test**

```python
def test_export_df_does_not_print(sample_df, io_dir, capsys):
    lp.export_df(sample_df, label="no_print", trace=False)
    captured = capsys.readouterr()
    assert captured.out == ""
```

- [ ] **Step 3:** Run + commit: `git commit -am "refactor(io): use logging instead of print (D4)"`

### Task 3: D6 — drop Py2 vestiges

- [ ] **Step 1:** In `src/lazypandas/__init__.py`, remove `from __future__ import absolute_import`.
- [ ] **Step 2:** In `src/lazypandas/io.py`, change `class Export(object):` → `class Export:` and `class Import(object):` → `class Import:`.
- [ ] **Step 3:** Run tests, commit: `git commit -am "refactor: drop Python 2 compatibility shims (D6)"`

### Task 4: D8 + H5 — populate `__all__`, prune dunders

- [ ] **Step 1: Modify `src/lazypandas/__init__.py`**

```python
__all__ = ["import_df", "export_df", "path_in", "path_out", "timestamp_label"]
__version__ = "0.2.0"  # single source of truth
# remove __author__ — it's in pyproject.toml now
```

- [ ] **Step 2:** Run tests, commit: `git commit -am "refactor: populate __all__, prune redundant dunders (D8, H5)"`

### Task 5: D7 — type hints on public API

- [ ] **Step 1: Modify `src/lazypandas/io.py`**

Add hints to method signatures:
```python
from typing import Any
import pandas as pd

class Export:
    def export_df(
        self,
        df: pd.DataFrame,
        label: str = "",
        show_index: bool = False,
        trace: bool = True,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        ...

class Import:
    def import_df(
        self,
        file_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> pd.DataFrame:
        ...
```
And add hints to property setters/getters (e.g., `def path_out(self) -> str:`).

- [ ] **Step 2: Modify `src/lazypandas/__init__.py` wrappers**

```python
def import_df(*args: Any, **kwargs: Any) -> pd.DataFrame:
    ...

def export_df(*args: Any, **kwargs: Any) -> None:
    ...
```

- [ ] **Step 3:** Run tests, commit: `git commit -am "refactor: add type hints to public API (D7)"`

### Task 6: D1 + D2 — drop singleton + shim layer

**Important:** This is the largest behavioral change in the chunk. Run full suite after each substep.

- [ ] **Step 1: Add a regression test that the public surface keeps working**

```python
def test_module_level_api_still_works(tmp_path, sample_df):
    """Set path via module attribute; call import/export via top-level functions."""
    lp.path_out = str(tmp_path)
    lp.path_in = str(tmp_path)
    lp.export_df(sample_df, label="moduleapi", trace=False)
    df = lp.import_df("moduleapi.csv")
    assert len(df) == 10
```

- [ ] **Step 2: Rewrite `src/lazypandas/io.py` without singletons**

Replace the `Export`/`Import` classes with a single `_State` dataclass + module-level functions:

```python
# src/lazypandas/io.py
import datetime
import glob
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

_TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S-"


@dataclass
class _State:
    path_in: str = "./"
    path_out: str = "./"
    timestamp_label: str = field(
        default_factory=lambda: datetime.datetime.now().strftime(_TIMESTAMP_FORMAT)
    )


state = _State()


def _validate_dir(value: str) -> str:
    if not Path(value).is_dir():
        raise NotADirectoryError(f"Not a valid directory: {value!r}")
    return value


def export_df(
    df: pd.DataFrame,
    label: str = "",
    show_index: bool = False,
    trace: bool = True,
    *args: Any,
    **kwargs: Any,
) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected DataFrame, got {type(df).__name__}")
    if not isinstance(label, str):
        raise TypeError(f"label must be str, got {type(label).__name__}")
    if not isinstance(show_index, bool):
        raise TypeError(f"show_index must be bool, got {type(show_index).__name__}")
    if not isinstance(trace, bool):
        raise TypeError(f"trace must be bool, got {type(trace).__name__}")

    label = label or "iteration_"
    out_dir = Path(_validate_dir(state.path_out))
    pattern = f"{state.timestamp_label}{label}*.csv"
    file_count = len(glob.glob(str(out_dir / pattern)))

    if trace:
        path = out_dir / f"{state.timestamp_label}{label}{file_count + 1}.csv"
    else:
        path = out_dir / f"{state.timestamp_label}{label}.csv"

    logger.info("Exporting to %s", path)
    try:
        df.to_csv(path_or_buf=str(path), index=show_index, *args, **kwargs)
    except Exception:
        logger.exception("Error writing CSV")
        raise

    if not path.is_file():
        raise IOError(f"Exported file not found: {path}")
    logger.info("Exported: %s", path)


def import_df(file_name: str, *args: Any, **kwargs: Any) -> pd.DataFrame:
    in_dir = Path(_validate_dir(state.path_in))
    all_files = sorted(glob.glob(str(in_dir / "*.csv")))
    if not all_files:
        logger.info("Import directory is empty: %s", in_dir)
        raise IOError(f"Import directory is empty: {in_dir}")

    matches = [y for y in all_files if file_name in y]
    if not matches:
        logger.error("No file matching %r in %s", file_name, in_dir)
        raise IndexError(f"No file matching {file_name!r} in {in_dir}")
    if len(matches) > 1:
        raise ValueError(
            f"ambiguous match for {file_name!r}: found {len(matches)} files: {matches}"
        )

    file = matches[0]
    df = pd.read_csv(file, low_memory=False, encoding="utf-8", *args, **kwargs)
    logger.info("Imported file: %s", file)
    logger.info("Total rows: %d", len(df))
    return df
```

- [ ] **Step 3: Rewrite `src/lazypandas/__init__.py` without shim**

```python
"""lazypandas — A collection of data wrangling helper methods for pandas."""

import logging

from . import io
from .io import import_df, export_df, state

logging.getLogger(__name__).addHandler(logging.NullHandler())

__version__ = "0.2.0"
__all__ = ["import_df", "export_df", "path_in", "path_out", "timestamp_label"]


# Module-level proxy attributes that read/write the shared state.
def __getattr__(name: str) -> str:
    if name in {"path_in", "path_out", "timestamp_label"}:
        return getattr(state, name)
    raise AttributeError(name)


def __setattr__(name: str, value: str) -> None:  # pragma: no cover — module-level setattr quirks
    if name in {"path_in", "path_out"}:
        # Trigger validation via io._validate_dir
        io._validate_dir(value)
        setattr(state, name, value)
    else:
        globals()[name] = value
```

**Note:** Python doesn't natively support module-level `__setattr__`. Alternative: simpler implementation — set `path_in`/`path_out` directly on `state`, document that users now use `lp.state.path_in = "..."`. Decide during implementation. **Recommended:** drop the magic and document the new API (`lp.state.path_in = ...`); update any tests + README accordingly. The regression test in Step 1 needs to be updated to use `lp.state.path_in = ...` if we take this route.

- [ ] **Step 4: Update tests to match new API**

If we keep module-level `lp.path_in = "..."` via setattr-by-convention, no change. If we move to `lp.state.path_in = "..."`, update every test (`tests/test_*.py`) and the README.

- [ ] **Step 5: Run full suite**: `.venv/bin/pytest -v` — all PASS.

- [ ] **Step 6: Commit**: `git commit -am "refactor: drop singleton pattern in favor of module-level state (D1, D2)"`

### Task 7: D3 — split `export_df` trace semantics

**Design:** Keep `export_df(trace=True/False)` as the backward-compatible entrypoint, but document that two named functions are the preferred path: `export_df_versioned` and `export_df_overwrite`. Add both as thin wrappers.

- [ ] **Step 1: Add wrappers in `src/lazypandas/io.py`**

```python
def export_df_versioned(df: pd.DataFrame, label: str = "", show_index: bool = False, *args: Any, **kwargs: Any) -> None:
    """Append a per-call version counter to the filename."""
    return export_df(df, label=label, show_index=show_index, trace=True, *args, **kwargs)


def export_df_overwrite(df: pd.DataFrame, label: str = "", show_index: bool = False, *args: Any, **kwargs: Any) -> None:
    """Overwrite a single file per label."""
    return export_df(df, label=label, show_index=show_index, trace=False, *args, **kwargs)
```

- [ ] **Step 2: Re-export from `__init__.py`**

Add to `__all__`: `"export_df_versioned"`, `"export_df_overwrite"`.

- [ ] **Step 3: Add tests in `tests/test_export_df.py`**

```python
def test_export_df_versioned(sample_df, io_dir):
    lp.export_df_versioned(sample_df, label="ver")
    lp.export_df_versioned(sample_df, label="ver")
    files = sorted(io_dir.glob(f"{lp.timestamp_label}ver*.csv"))
    assert len(files) == 2


def test_export_df_overwrite(sample_df, io_dir):
    lp.export_df_overwrite(sample_df, label="over")
    lp.export_df_overwrite(sample_df, label="over")
    files = list(io_dir.glob(f"{lp.timestamp_label}over.csv"))
    assert len(files) == 1
```

- [ ] **Step 4:** Run + commit: `git commit -am "feat(io): add export_df_versioned and export_df_overwrite wrappers (D3)"`

### Task 8: B5 — document session-shared timestamp

- [ ] **Step 1: Add a docstring + README note**

In `src/lazypandas/io.py`, document `_State.timestamp_label`:
```python
timestamp_label: str = field(
    default_factory=lambda: datetime.datetime.now().strftime(_TIMESTAMP_FORMAT)
)
# NOTE: timestamp_label is computed once at module import and shared across
# all exports in a session. To rotate it, reassign lp.state.timestamp_label
# (or call lp.io._State() to start a fresh session).
```

- [ ] **Step 2:** Add a section to README.md under "Configuration" describing this.

- [ ] **Step 3:** Commit: `git commit -am "docs(io): document session-shared timestamp_label behavior (B5)"`

### Task 9: P5 — add ruff

- [ ] **Step 1: Append to `pyproject.toml`**

```toml
[tool.ruff]
line-length = 100
target-version = "py310"
src = ["src", "tests"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP", "RUF"]
ignore = ["E501"]  # line length handled by formatter

[tool.ruff.format]
quote-style = "double"
```

- [ ] **Step 2: Install + run**

```bash
uv pip install ruff
.venv/bin/ruff check .
.venv/bin/ruff format --check .
```
Fix any reported issues (or run `ruff format .` and `ruff check --fix .`).

- [ ] **Step 3:** Run `.venv/bin/pytest -v` — still PASS.

- [ ] **Step 4:** Add ruff to `[project.optional-dependencies].dev`:

```toml
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.6", "mypy>=1.10"]
```

- [ ] **Step 5:** Commit: `git commit -am "build: add ruff lint + format config (P5)"`

### Task 10: P6 — add mypy

- [ ] **Step 1: Append to `pyproject.toml`**

```toml
[tool.mypy]
python_version = "3.10"
strict = true
files = ["src/lazypandas"]
```

- [ ] **Step 2: Run**: `.venv/bin/mypy src/lazypandas` — fix any errors (most likely missing `pandas-stubs`):

```bash
uv pip install pandas-stubs
```

- [ ] **Step 3:** Add `pandas-stubs` to dev deps.

- [ ] **Step 4:** Commit: `git commit -am "build: add mypy strict mode (P6)"`

### Task 11: P8 — pre-commit

- [ ] **Step 1: Create `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.2
    hooks:
      - id: mypy
        files: ^src/
        additional_dependencies: [pandas-stubs]
```

- [ ] **Step 2: Test locally**

```bash
uv pip install pre-commit
.venv/bin/pre-commit run --all-files
```
Expected: all hooks pass (after fixing any reported issues).

- [ ] **Step 3:** Commit: `git commit -am "build: add pre-commit hooks for ruff + mypy (P8)"`

### Task 12: Add lint + type-check to CI workflow

- [ ] **Step 1: Modify `.github/workflows/ci.yml`** — add a lint job:

```yaml
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: |
          uv venv --python 3.11 .venv
          uv pip install --python .venv/bin/python -e ".[dev]"
      - run: .venv/bin/ruff check .
      - run: .venv/bin/ruff format --check .
      - run: .venv/bin/mypy src/lazypandas
```

- [ ] **Step 2:** Commit: `git commit -am "ci: add lint + type-check job"`

### Task 13: chunk-polish review + merge

- [ ] **Step 1:** Run full suite, ruff, mypy — all green.
- [ ] **Step 2:** Invoke `superpowers:requesting-code-review`. Reviewer: **Claude**.
- [ ] **Step 3:** Address review.
- [ ] **Step 4:** Confirm → push → PR `refactor: code style cleanup, type hints, ruff + mypy + pre-commit` → squash-merge.

---

# Final pass

## Task: integration review across master

- [ ] **Step 1:** `git checkout master && git pull` — ensure all 6 chunk PRs are merged.
- [ ] **Step 2:** Run full suite: `.venv/bin/pytest -v` — all green.
- [ ] **Step 3:** Run lint + type-check: `.venv/bin/ruff check . && .venv/bin/mypy src/lazypandas` — green.
- [ ] **Step 4:** Verify GitHub Actions CI is green on master.
- [ ] **Step 5:** Invoke `superpowers:requesting-code-review` on the diff `master ↔ pre-modernization-tag` (or just `master ↔ 3924d37` — the spec commit). Reviewer: **both Claude and codex** — submit independently.
- [ ] **Step 6:** Address any final review comments via a `chore:` PR if material.
- [ ] **Step 7:** Tag release:

```bash
git tag -a v0.2.0 -m "v0.2.0: modernization release"
# CONFIRM WITH USER BEFORE PUSHING TAG
git push origin v0.2.0
```

- [ ] **Step 8:** Update CHANGELOG to mark `[Unreleased]` → `[0.2.0] — 2026-XX-XX`.

---

## Self-review checklist (writing-plans skill)

**Spec coverage:** Every ID from spec is mapped:
- Bugs B1–B6: covered in chunk-bugs (B5 deferred to chunk-polish Task 8, intentional per spec).
- Design D1–D8: covered in chunk-polish Tasks 1–7.
- Tests T1–T7: covered in chunk-tests.
- Packaging P1–P9: P1/P2/P3/P4/P9 in chunk-pkg, P5/P6/P8 in chunk-polish, P7 in chunk-ci.
- Hygiene H1–H5: H1/H2/H4 in chunk-readme, H3 in chunk-tests, H5 in chunk-polish Task 4.

**Placeholder scan:** No "TBD", "TODO", or "add error handling" stubs. All code shown inline. The one judgment-call note (chunk-polish Task 6 Step 3 about module `__setattr__`) is explicit about the recommendation.

**Type consistency:** `export_df` / `import_df` signatures consistent across spec, bugs chunk (which doesn't change signatures), and polish chunk (which adds hints and wrappers).

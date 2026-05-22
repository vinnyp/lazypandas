# lazypandas modernization — design spec

**Status:** approved, ready for implementation plan
**Date:** 2026-05-22
**Owner:** Vinny Pasceri
**Scope:** Modernize and revive the 2018-era `lazypandas` library so it runs cleanly on current Python/pandas, has correct behavior, and uses modern packaging.

## Context

`lazypandas` is a small helper library (one module, ~135 LOC; two test files) providing two functions:

- `import_df(file_name, ...)` — load a CSV from `path_in` by substring match on filename.
- `export_df(df, label='', show_index=False, trace=True, ...)` — write a DataFrame to `path_out` with a session-shared timestamp prefix. `trace=True` appends a version counter; `trace=False` overwrites.

Last touched in 2018. Installs cleanly today under Python 3.11 + pandas 3.0.3 + numpy 2.4.6. **9 of 10 tests pass**; the single failure (`test_file_not_found`) is a latent bug, not a compatibility problem.

The goal is "modernize and revive": fix the bugs, modernize the toolchain, leave the public API mostly intact.

## Findings

Organized by severity. Each finding has an ID used by the implementation plan.

### Bugs (broken behavior)

| ID | Location | Issue |
|---|---|---|
| **B1** | `io.py:130` | `len(file)` logs the filename string length instead of `len(df)`. |
| **B2** | `io.py:132` | `self.logger.exception('No file found with that name.', e)` treats `e` as a `%`-format arg, raises `TypeError`, masks the real `IndexError`. This is the cause of the failing test. |
| **B3** | `io.py:74, 81` | `self.logger.exception(self, "Exception: ", e)` — wrong signature, `self` becomes the message. Crashes on any real exception. |
| **B4** | `io.py:71, 78` | Output paths built by string concatenation (`self.path_out + ...`). Breaks if `path_out` doesn't end in `/`. |
| **B5** | `io.py:11-12` | `_timestamp_now` computed at class-definition time, so all exports in a session share one timestamp. Tests depend on this; behavior is undocumented and surprising. |
| **B6** | `io.py:127` | `import_df` uses fuzzy `if file_name in y` substring matching and silently pops the last match. Two files matching the substring → wrong one loaded silently. |

### API & design

| ID | Suggestion |
|---|---|
| **D1** | Drop singleton-with-`__new__` pattern in `Export`/`Import`. Plain module-level functions (or one small config object) do the same job. |
| **D2** | Drop the `__init__.py` rebind/copy-back shim. Module-level functions with explicit `path` kwargs are clearer. |
| **D3** | Split `export_df(trace=True/False)` into two clearer ideas: append-versioned vs. overwrite. |
| **D4** | Replace `print('Exported: ...')` with logging — it's a library. |
| **D5** | Path-setter raises `TypeError("Not a valid path")` — use `NotADirectoryError` or `ValueError`. |
| **D6** | Remove Py2 vestiges: `from __future__ import absolute_import`, `class Foo(object):`. |
| **D7** | Add type hints throughout. |
| **D8** | `__all__ = []` is empty but the wrappers are public — populate it. |

### Tests

| ID | Suggestion |
|---|---|
| **T1** | `tests/test_import_df.py` class is misnamed `TestExportDf` (copy-paste). Rename. |
| **T2** | Drop `unittest.TestCase`; mixes uneasily with pure pytest functions. Use pytest functions. |
| **T3** | Replace `setUp`'s 15-line logger boilerplate with `caplog` fixture or just delete. |
| **T4** | Use `tmp_path` fixture instead of writing into tracked `tests/file_output/`. |
| **T5** | Assert exported file *contents* match input via `pd.read_csv` + `assert_frame_equal`. |
| **T6** | Add a test for multi-match behavior of `import_df` (covers B6 once fixed). |
| **T7** | Add `pytest-cov` and a coverage gate. |

### Packaging / tooling

| ID | Suggestion |
|---|---|
| **P1** | Migrate `setup.py` → `pyproject.toml` (PEP 621). |
| **P2** | Bump declared deps to `pandas>=2.2`, `numpy>=1.26`. |
| **P3** | `requires-python = ">=3.10"`, update classifiers. |
| **P4** | Delete `tox.ini`; pytest config in `[tool.pytest.ini_options]`. |
| **P5** | Add `ruff` (lint + format) in `pyproject.toml`. |
| **P6** | Add `mypy` once D7 lands. |
| **P7** | GitHub Actions workflow: matrix py3.10/3.11/3.12/3.13 × pandas 2.x/3.x. |
| **P8** | `pre-commit` config for ruff + mypy. |
| **P9** | Switch to `src/` layout (`src/lazypandas/`). |

### Repo hygiene

| ID | Suggestion |
|---|---|
| **H1** | Rewrite `README.rst` as `README.md` with real content and working badges (or remove badges). |
| **H2** | Add `CHANGELOG.md`; single-source-of-truth `__version__`. |
| **H3** | Delete empty `tests/__init__.py` if rootdir-based pytest discovery. |
| **H4** | Scope `.gitignore` `*.csv` rule to test output dir. |
| **H5** | Remove `__author__`, redundant dunders once D1/D2 land. |

## Implementation strategy

### Approach: DAG of chunks executed in two waves

Chunks are not fully independent. The DAG:

```
Wave 1 (parallel) — LANDED:
  - chunk-bugs    (B1, B2, B3, B4, B6 — strict TDD)            ✅ #4
  - chunk-pkg     (P1, P2, P3, P4, P9 — pyproject + src/)      ✅ #6
  - chunk-readme  (H1, H2, H4 — README + CHANGELOG + gitignore) ✅ #5

Wave 2 (parallel where DAG allows):
  - chunk-tests    (T1, T2, T3, T4, T5, T6, T7 — pytest cleanup)
  - chunk-ci       (P7 — GitHub Actions matrix)
  - chunk-polish   (D1-D8, P5, P6, P8, H3, H5, B5 doc, zfill counter)
  - chunk-examine  (E1, E2 — port missing_summary + missing_values)
  - chunk-actions  (A1 — port split_and_fill with TDD)
```

`B5` (session-shared timestamp) is intentionally deferred: the behavior is depended on by current tests; revisit during `chunk-polish` and decide whether to document it as-is or change it (probably document — changing it is a public-API change).

### Additional findings from `feature_describefunctions` (8-year-old branch, audited 2026-05-22)

| ID | Source commit | Description |
|---|---|---|
| **E1** | `93faff7` | Port `missing_summary(df) -> Series` — per-column count of missing values. Modernize: type hints, fix broken `logger.exception("msg", e)` signature, return type clear. |
| **E2** | `93faff7` | Port `missing_values(df, columns=None) -> int` — scalar count of nulls across df or column subset. Same modernization. |
| **A1** | `70594ec` | Port `split_and_fill(df, source, target, separator) -> DataFrame` — backfills empty target column by splitting source on a separator. **WIP, no tests** in the original — write tests TDD-style before landing. |
| (folded) | `93faff7` | `.zfill(2)` on trace counter → `iteration_01.csv` vs `iteration_1.csv`. Folded into `chunk-polish`. |
| (skipped) | `93faff7` | `unique()` stub raising `NotImplementedError` — empty, dropped. |
| (skipped) | `e4574dc` | `len(file)` → `len(df)` — duplicate of B1, already fixed. |
| (skipped) | `e4574dc` | Extra `logger.info(df.dtypes)` per import — too noisy by default. |

### Per-chunk workflow

1. Create a worktree at `../lazypandas-<chunk>/` on branch `chunk/<name>`.
2. Dispatch implementation to either a Claude subagent OR `codex exec --cd <worktree>` (alternate per chunk for variety).
3. **Strict TDD for bug fixes** — write the failing test first, then fix.
4. Verify locally: `.venv/bin/pytest -v` in the worktree.
5. `superpowers:requesting-code-review` — alternate reviewer model from the implementer.
6. Address review comments; re-verify.
7. User-confirm before push.
8. Push branch, open PR with conventional-commit title (`fix:`, `chore:`, `refactor:`, etc.), merge.

### Final pass

After all chunks land on `master`:

- Run `superpowers:requesting-code-review` across the combined result to catch integration-level issues.
- Cut `v0.2.0` release tag.

## Conventions

- **Commits:** [Conventional Commits](https://www.conventionalcommits.org/) — `fix:`, `feat:`, `chore:`, `refactor:`, `docs:`, `test:`, `build:`, `ci:`.
- **Branches:** `chunk/<name>` (e.g., `chunk/bugs`, `chunk/pkg`).
- **PRs:** one per chunk, target `master`, squash-merge.
- **Issues:** none — PR descriptions carry context.
- **Reviewers:** alternate Claude / codex per branch; final pass reviewed by both.
- **Environment:** `uv` with Python 3.11 at `.venv/`.

## Out of scope

- Renaming the package or changing the public API beyond the small renames captured under `D3`.
- Publishing to PyPI (gated separately after `v0.2.0`).
- Adding new features beyond the audit.
- Migrating CI to anything other than GitHub Actions.

## Success criteria

- All 10 existing tests pass (plus new tests added per T-section, E-section, A-section).
- `uv pip install -e .` installs cleanly using `pyproject.toml`.
- `ruff check` passes; `mypy` passes (if D7 lands).
- GitHub Actions CI green on at least py3.11 × pandas 3.x.
- `README.md` renders correctly on GitHub with no broken badges.
- All 6 bugs (B1–B6) have a regression test.
- `missing_summary`, `missing_values`, and `split_and_fill` all have test coverage.

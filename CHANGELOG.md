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
- `export_df_versioned` and `export_df_overwrite` convenience wrappers around `export_df` (D3).
- Zero-padded trace counter (`iteration_01.csv` rather than `iteration_1.csv`) for filesystem sort order.
- `missing_summary(df) -> Series` and `missing_values(df, columns=None) -> int` in new `examine` module (E1, E2).
- `split_and_fill(df, source, target, separator)` in new `actions` module (A1).
- `ruff`, `mypy --strict`, and `pre-commit` tooling (P5, P6, P8).

### Changed
- **BREAKING**: configuration moved from module-level attributes to a single `state` object. `lazypandas.path_in = "..."` is now `lazypandas.state.path_in = "..."` (similarly `path_out` and `timestamp_label`). The singleton `Export` / `Import` classes are removed (D1, D2).
- `import_df` now raises `ValueError` on ambiguous substring matches (was: silently picked one).
- `export_df` paths now built via `pathlib` (was: string concatenation, broke without trailing slash).
- `logger.exception` calls fixed to propagate real exceptions instead of `TypeError`.
- Invalid paths now raise `NotADirectoryError` instead of `TypeError` (D5).
- `export_df` uses logging instead of `print` (D4).

### Removed
- `setup.py`, `tox.ini`, `README.rst`.
- `Export` and `Import` singleton classes (D1).
- Python 2 compatibility shims (`from __future__ import absolute_import`, `class Foo(object):`) (D6).

## [0.1.0] — 2018-06-30

- Initial release.

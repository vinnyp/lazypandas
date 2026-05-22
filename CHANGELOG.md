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

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

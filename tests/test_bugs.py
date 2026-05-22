import pandas as pd
import numpy as np
import pytest
import lazypandas as lp


def _sample_df():
    return pd.DataFrame(np.random.randn(5, 2), columns=["A", "B"])


def test_b2_import_df_missing_file_raises_indexerror(tmp_path):
    """B2: logger.exception was wrapping IndexError into TypeError."""
    # Seed the import dir with one unrelated csv so the directory is not empty.
    # Write directly with pandas to avoid relying on export_df (which has B4 path bug
    # fixed in a later task).
    _sample_df().to_csv(tmp_path / "seed.csv", index=False)
    lp.path_in = str(tmp_path)
    lp.path_out = str(tmp_path)

    with pytest.raises(IndexError):
        lp.import_df("not_a_real_file.csv")

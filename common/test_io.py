"""Small tests that check my file helpers save and load correctly."""

import pandas as pd

from common.io import save_parquet, load_parquet, save_csv, ensure_dir


def test_parquet_round_trip(tmp_path):
    # I will save a small table and load it back
    df = pd.DataFrame({"a": [1, 2, 3], "b": [0.1, 0.2, 0.3]})
    save_parquet(df, tmp_path / "sub" / "demo.parquet")
    loaded = load_parquet(tmp_path / "sub" / "demo.parquet")

    # I expect the loaded table to match what I saved
    assert df.equals(loaded)


def test_load_missing_file_gives_clear_error(tmp_path):
    # I expect a clear error for a file that does not exist
    try:
        load_parquet(tmp_path / "missing.parquet")
        assert False, "I expected a FileNotFoundError"
    except FileNotFoundError:
        pass


def test_save_csv_and_ensure_dir(tmp_path):
    # I will save a CSV into a folder that does not exist yet
    df = pd.DataFrame({"x": [1, 2]})
    save_csv(df, tmp_path / "new_folder" / "out.csv")

    # I expect the folder and file to exist
    assert ensure_dir(tmp_path / "new_folder").exists()
    assert (tmp_path / "new_folder" / "out.csv").exists()
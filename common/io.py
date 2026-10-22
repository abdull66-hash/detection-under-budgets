"""Shared file helpers so all my projects load and save data the same way."""

from pathlib import Path

import pandas as pd

# I will find the repo root from the location of this file
REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"


def ensure_dir(path):
    """I will create a folder if it does not exist yet, then return it."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_parquet(df, path):
    """I will save a dataframe as parquet, making the folder if needed."""
    path = Path(path)
    ensure_dir(path.parent)
    df.to_parquet(path, index=False)


def load_parquet(path):
    """I will load a parquet file and give a clear error if it is missing."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"I could not find {path}. Did I run the download step?")
    return pd.read_parquet(path)


def save_csv(df, path):
    """I will save a dataframe as CSV, making the folder if needed."""
    path = Path(path)
    ensure_dir(path.parent)
    df.to_csv(path, index=False)
"""Load the NF-UNSW-NB15-v2 CSV once and save a fast parquet copy."""

from pathlib import Path

import pandas as pd

from common.io import DATA_DIR, save_parquet

# I save the parquet copy here (data/ is ignored by git)
PARQUET_PATH = DATA_DIR / "processed" / "nf_unsw_nb15_v2.parquet"


def find_csv():
    """I search the data folder for the CSV, so I do not hard-code the long path."""
    matches = list(Path(DATA_DIR).rglob("NF-UNSW-NB15-v2.csv"))
    if not matches:
        raise FileNotFoundError("I could not find NF-UNSW-NB15-v2.csv inside data/")
    return matches[0]


def main():
    # I read the whole CSV into a table
    csv_path = find_csv()
    df = pd.read_csv(csv_path, low_memory=False)

    # I save a parquet copy so later steps load much faster
    save_parquet(df, PARQUET_PATH)

    # I print the facts I need to verify
    print("rows, columns:", df.shape)
    print("memory (MB):", round(df.memory_usage(deep=True).sum() / 1e6, 1))
    print("\nLabel counts:")
    print(df["Label"].value_counts())
    print("\nAttack counts:")
    print(df["Attack"].value_counts())


if __name__ == "__main__":
    main()
"""Load, clean and prepare the data for the models."""

from pathlib import Path
from sklearn.model_selection import train_test_split

import numpy as np
import pandas as pd
import yaml

from common.io import load_parquet, REPO_ROOT

# Path to the settings file
CONFIG_PATH = Path(__file__).resolve().parent.parent / "configs" / "p1.yaml"


def load_config():
    # Read the settings file
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def load_clean_data(config):
    # Load the saved parquet file
    df = load_parquet(REPO_ROOT / config["dataset"]["parquet"])

    # Remove duplicate rows
    df = df.drop_duplicates().reset_index(drop=True)

    # Turn infinite values into missing values, then remove those rows
    df = df.replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
    return df


def get_feature_columns(df, config, run="main"):
    # Columns that are never used as features
    drop = set(config["excluded_features"])

    # The main run also drops the TTL columns
    if run == "main":
        drop |= set(config["main_run_drop"])

    # Everything else is a feature
    return [c for c in df.columns if c not in drop]

def split_data(df, config):
    # Read the split settings
    seed = config["split"]["seed"]
    test_size = config["split"]["test_size"]
    scorer_size = config["split"]["scorer_size"]

    # First cut: take out the test set
    rest, test = train_test_split(
        df, test_size=test_size, random_state=seed, stratify=df["Attack"]
    )

    # Second cut: take the scorer set out of the rest
    scorer_share = scorer_size / (1 - test_size)
    train, scorer = train_test_split(
        rest, test_size=scorer_share, random_state=seed, stratify=rest["Attack"]
    )

    # The original row numbers are kept, so the parts can be checked for overlap
    return train, scorer, test
"""Train the baseline models on the full data and save the results."""

import argparse
import time

import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.metrics import false_positive_rate, macro_f1, pr_auc, recall_score_binary
from common.seed import set_all_seeds
from p1_monitoring_budget.src.models import build_model
from p1_monitoring_budget.src.preprocess import (
    get_feature_columns,
    load_clean_data,
    load_config,
    split_data,
)

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# The two feature sets and the three models
RUNS = ["main", "sensitivity"]
MODELS = ["logreg", "random_forest", "lightgbm"]


def score_model(model, test, cols):
    # Attack score and predicted label for every test flow
    y_true = test["Label"].to_numpy()
    scores = model.predict_proba(test[cols])[:, 1]
    y_pred = (scores >= 0.5).astype(int)

    # Overall metrics
    row = {
        "recall": recall_score_binary(y_true, y_pred),
        "fpr": false_positive_rate(y_true, y_pred),
        "pr_auc": pr_auc(y_true, scores),
        "macro_f1": macro_f1(y_true, y_pred),
    }

    # Share of each attack class that is flagged as an attack
    for attack in sorted(test["Attack"].unique()):
        if attack == "Benign":
            continue
        flagged = y_pred[(test["Attack"] == attack).to_numpy()]
        row["recall_" + attack] = float(flagged.mean())
    return row


def run_baseline(quick=False):
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)

    # Quick mode: one seed and a smaller training set
    seeds = [0] if quick else config["seeds"]
    if quick:
        train = train.sample(100_000, random_state=0)

    rows = []
    for run in RUNS:
        cols = get_feature_columns(df, config, run)
        for name in MODELS:
            for seed in seeds:
                # Train the model and time it
                set_all_seeds(seed)
                model = build_model(name, config, seed)
                start = time.time()
                model.fit(train[cols], train["Label"])
                seconds = time.time() - start

                # Score it on the test set
                row = {"run": run, "model": name, "seed": seed, "fit_seconds": round(seconds, 1)}
                row.update(score_model(model, test, cols))
                rows.append(row)
                print(run, name, seed, "recall", round(row["recall"], 4), "fpr", round(row["fpr"], 5))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="one seed, small training set, nothing saved")
    args = parser.parse_args()

    results = run_baseline(quick=args.quick)
    if args.quick:
        print(results.round(4).to_string(index=False))
    else:
        save_csv(results, RESULTS_DIR / "baseline_raw.csv")
        print("Saved baseline_raw.csv")
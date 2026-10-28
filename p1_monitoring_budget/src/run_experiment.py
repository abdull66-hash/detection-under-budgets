"""Regime (i): train on full data, test on sampled data."""

import argparse
import time

import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.metrics import macro_f1, pr_auc
from common.seed import set_all_seeds
from p1_monitoring_budget.src.models import build_model
from p1_monitoring_budget.src.preprocess import (
    get_feature_columns,
    load_clean_data,
    load_config,
    split_data,
)
from p1_monitoring_budget.src.sampling import make_mask

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Feature sets and models
RUNS = ["main", "sensitivity"]
MODELS = ["logreg", "random_forest", "lightgbm"]


def build_masks(test, config, seeds):
    # Policies built so far (attack_aware comes on Day 4)
    policies = [p for p in config["sampling"]["policies"] if p != "attack_aware"]

    # One mask for every policy, budget and seed. Masks do not depend on the model.
    masks = {}
    for seed in seeds:
        for policy in policies:
            for budget in config["budgets"]:
                masks[(policy, budget, seed)] = make_mask(policy, test, budget, seed, config)
        print("masks ready for seed", seed)
    return policies, masks


def run_regime_one(quick=False):
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)

    # Quick mode: one seed and a smaller training set
    seeds = [0] if quick else config["seeds"]
    if quick:
        train = train.sample(100_000, random_state=0)

    # Test labels and one True/False list per attack class
    y_true = test["Label"].to_numpy()
    attack_classes = sorted(c for c in test["Attack"].unique() if c != "Benign")
    class_index = {c: (test["Attack"] == c).to_numpy() for c in attack_classes}

    policies, masks = build_masks(test, config, seeds)

    rows = []
    for run in RUNS:
        cols = get_feature_columns(df, config, run)
        for name in MODELS:
            for seed in seeds:
                # Train once on the full training set and score the test set once
                set_all_seeds(seed)
                model = build_model(name, config, seed)
                start = time.time()
                model.fit(train[cols], train["Label"])
                scores = model.predict_proba(test[cols])[:, 1]
                flagged_all = scores >= 0.5
                print(run, name, seed, "trained in", round(time.time() - start), "s")

                for policy in policies:
                    for budget in config["budgets"]:
                        mask = masks[(policy, budget, seed)]

                        # A flow that is not sampled is not flagged
                        flagged = flagged_all & mask

                        row = {
                            "run": run, "model": name, "seed": seed,
                            "policy": policy, "budget": budget,
                            "realized_rate": float(mask.mean()),
                            "n_sampled": int(mask.sum()),
                            "attack_visible": float(mask[y_true == 1].mean()),
                            # Recall and false positive rate over ALL test flows
                            "recall": float(flagged[y_true == 1].mean()),
                            "fpr": float(flagged[y_true == 0].mean()),
                            # Unsampled flows get score 0
                            "pr_auc": pr_auc(y_true, scores * mask),
                            "macro_f1": macro_f1(y_true, flagged.astype(int)),
                        }
                        for c in attack_classes:
                            row["recall_" + c] = float(flagged[class_index[c]].mean())
                        rows.append(row)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="one seed, small training set, nothing saved")
    args = parser.parse_args()

    results = run_regime_one(quick=args.quick)
    if args.quick:
        # Show recall and realized rate for one model
        part = results[(results["run"] == "main") & (results["model"] == "random_forest")]
        print(part.pivot(index="policy", columns="budget", values="recall").round(4).to_string())
        print(part.pivot(index="policy", columns="budget", values="realized_rate").round(5).to_string())
    else:
        save_csv(results, RESULTS_DIR / "regime1_raw.csv")
        print("Saved regime1_raw.csv with", len(results), "rows")
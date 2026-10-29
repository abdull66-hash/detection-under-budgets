"""Regime (i): train on full data, test on sampled data."""

import argparse
import time

import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.metrics import macro_f1, pr_auc
from common.seed import set_all_seeds
from p1_monitoring_budget.src.campaigns import campaign_detection, make_campaign_ids
from p1_monitoring_budget.src.models import build_model
from p1_monitoring_budget.src.preprocess import (
    get_feature_columns,
    load_clean_data,
    load_config,
    split_data,
)
from p1_monitoring_budget.src.sampling import (
    attack_aware_mask,
    make_mask,
    suspicion_scores,
    train_scorer,
)

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Feature sets and models
RUNS = ["main", "sensitivity"]
MODELS = ["logreg", "random_forest", "lightgbm"]


def build_masks(test, scorer, config, seeds):
    policies = config["sampling"]["policies"]
    floor = config["sampling"]["suspicion_floor"]

    # One mask for every policy, budget and seed. Masks do not depend on the model.
    masks = {}
    for seed in seeds:
        # The cheap scorer is trained on the scorer split, then scores the test flows
        tree = train_scorer(scorer, config, seed)
        suspicion = suspicion_scores(tree, test, config)

        for policy in policies:
            for budget in config["budgets"]:
                if policy == "attack_aware":
                    mask = attack_aware_mask(suspicion, budget, seed, floor)
                else:
                    mask = make_mask(policy, test, budget, seed, config)
                masks[(policy, budget, seed)] = mask
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

    # Campaigns in the test set, with the two definitions
    cc = config["campaigns"]
    ids_p, k_p = make_campaign_ids(test, cc["primary_columns"], cc["min_flows"])
    ids_c, k_c = make_campaign_ids(test, cc["coarse_columns"], cc["min_flows"])
    print("campaigns in the test set: primary", k_p, "| coarse", k_c)

    policies, masks = build_masks(test, scorer, config, seeds)

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
                            # Campaign detected = at least one flow sampled and flagged
                            "campaign_primary": campaign_detection(ids_p, k_p, flagged),
                            "campaign_coarse": campaign_detection(ids_c, k_c, flagged),
                            # Campaign visible = at least one flow sampled (the ceiling)
                            "campaigns_visible_primary": campaign_detection(ids_p, k_p, mask),
                            "campaigns_visible_coarse": campaign_detection(ids_c, k_c, mask),
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
        # Show a few columns for one model
        part = results[(results["run"] == "main") & (results["model"] == "random_forest")]
        for column in ["recall", "campaign_primary", "campaign_coarse", "realized_rate"]:
            print(column)
            print(part.pivot(index="policy", columns="budget", values=column).round(4).to_string())
    else:
        save_csv(results, RESULTS_DIR / "regime1_raw.csv")
        print("Saved regime1_raw.csv with", len(results), "rows")
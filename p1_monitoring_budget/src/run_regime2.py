"""Regime (ii): train and test on sampled data."""

import argparse
import time

import numpy as np
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
from p1_monitoring_budget.src.run_experiment import build_masks
from p1_monitoring_budget.src.sampling import (
    attack_aware_mask,
    make_mask,
    suspicion_scores,
    train_scorer,
)

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Models for the full run
MODELS = ["logreg", "random_forest", "lightgbm"]


def build_train_masks(train, scorer, config, seed):
    floor = config["sampling"]["suspicion_floor"]

    # The cheap scorer is trained on the scorer split and scores the training flows
    tree = train_scorer(scorer, config, seed)
    suspicion = suspicion_scores(tree, train, config)

    masks = {}
    for policy in config["sampling"]["policies"]:
        for budget in config["budgets"]:
            # Budget 1.0 is the same as regime (i)
            if budget >= 1.0:
                continue

            # Host-keyed keeps the same hash. The other policies use another random stream.
            train_seed = seed if policy == "host_keyed" else seed + 1000
            if policy == "attack_aware":
                masks[(policy, budget)] = attack_aware_mask(suspicion, budget, train_seed, floor)
            else:
                masks[(policy, budget)] = make_mask(policy, train, budget, train_seed, config)
    return masks


def run_regime_two(quick=False):
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    cols = get_feature_columns(df, config, "main")
    min_class = config["training"]["min_class_flows"]

    # Quick mode: one seed and one model
    seeds = [0] if quick else config["seeds"]
    models = ["random_forest"] if quick else MODELS

    # Test labels and one True/False list per attack class
    y_true = test["Label"].to_numpy()
    attack_classes = sorted(c for c in test["Attack"].unique() if c != "Benign")
    class_index = {c: (test["Attack"] == c).to_numpy() for c in attack_classes}

    # Campaigns in the test set, with the two definitions
    cc = config["campaigns"]
    ids_p, k_p = make_campaign_ids(test, cc["primary_columns"], cc["min_flows"])
    ids_c, k_c = make_campaign_ids(test, cc["coarse_columns"], cc["min_flows"])

    # Test masks are the same as in regime (i)
    policies, test_masks = build_masks(test, scorer, config, seeds)

    rows = []
    for seed in seeds:
        train_masks = build_train_masks(train, scorer, config, seed)
        for name in models:
            for policy in policies:
                start = time.time()
                for budget in config["budgets"]:
                    if budget >= 1.0:
                        continue

                    # The sampled training set
                    sample = train[train_masks[(policy, budget)]]
                    n_attack = int(sample["Label"].sum())
                    n_benign = len(sample) - n_attack
                    trained = n_attack >= min_class and n_benign >= min_class

                    # Train on the sample and score the test set. Without a model nothing is flagged.
                    if trained:
                        set_all_seeds(seed)
                        model = build_model(name, config, seed)
                        model.fit(sample[cols], sample["Label"])
                        scores = model.predict_proba(test[cols])[:, 1]
                    else:
                        scores = np.zeros(len(test))

                    # A flow that is not sampled is not flagged
                    mask = test_masks[(policy, budget, seed)]
                    flagged = (scores >= 0.5) & mask

                    row = {
                        "regime": 2, "run": "main", "model": name, "seed": seed,
                        "policy": policy, "budget": budget,
                        "train_n": len(sample), "train_attack": n_attack, "trained": trained,
                        "realized_rate": float(mask.mean()),
                        "n_sampled": int(mask.sum()),
                        "attack_visible": float(mask[y_true == 1].mean()),
                        "recall": float(flagged[y_true == 1].mean()),
                        "fpr": float(flagged[y_true == 0].mean()),
                        "pr_auc": pr_auc(y_true, scores * mask),
                        "macro_f1": macro_f1(y_true, flagged.astype(int)),
                        "campaign_primary": campaign_detection(ids_p, k_p, flagged),
                        "campaign_coarse": campaign_detection(ids_c, k_c, flagged),
                        "campaigns_visible_primary": campaign_detection(ids_p, k_p, mask),
                        "campaigns_visible_coarse": campaign_detection(ids_c, k_c, mask),
                    }
                    for c in attack_classes:
                        row["recall_" + c] = float(flagged[class_index[c]].mean())
                    rows.append(row)
                print("seed", seed, name, policy, "done in", round(time.time() - start), "s")

        # Save after every seed, so a crash does not lose everything
        if not quick:
            save_csv(pd.DataFrame(rows), RESULTS_DIR / "regime2_raw.csv")

    results = pd.DataFrame(rows)

    # Add the budget 1.0 rows from regime (i): the same experiment
    if not quick:
        full = pd.read_csv(RESULTS_DIR / "regime1_raw.csv")
        full = full[(full["run"] == "main") & (full["budget"] >= 1.0)].copy()
        full["regime"] = 2
        full["train_n"] = len(train)
        full["train_attack"] = int(train["Label"].sum())
        full["trained"] = True
        results = pd.concat([results, full], ignore_index=True)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="one seed, random forest only, nothing saved")
    args = parser.parse_args()

    results = run_regime_two(quick=args.quick)
    if args.quick:
        for column in ["recall", "campaign_primary", "train_attack", "trained"]:
            print(column)
            print(results.pivot(index="policy", columns="budget", values=column).round(4).to_string())
    else:
        save_csv(results, RESULTS_DIR / "regime2_raw.csv")
        print("Saved regime2_raw.csv with", len(results), "rows")
"""Look inside the attack-aware scorer. Prints tables only. Writes nothing."""

import numpy as np
import pandas as pd
from sklearn.tree import export_text

from common.io import REPO_ROOT
from p1_monitoring_budget.src.preprocess import load_clean_data, load_config, split_data
from p1_monitoring_budget.src.sampling import attack_aware_mask, suspicion_scores, train_scorer

# Folder with the saved results
R = REPO_ROOT / "p1_monitoring_budget" / "results"


def keep_probabilities(suspicion, budget, floor):
    # Same steps as attack_aware_mask, but it returns the keep probability of every flow
    weight = floor + (1 - floor) * suspicion
    target = budget * len(suspicion)
    low, high = 0.0, 1.0 / weight.min()
    for _ in range(60):
        mid = (low + high) / 2
        if np.minimum(1.0, mid * weight).sum() < target:
            low = mid
        else:
            high = mid
    return np.minimum(1.0, high * weight), high


def main():
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    columns = config["sampling"]["scorer_features"]
    floor = config["sampling"]["suspicion_floor"]

    # Train the scorer for seeds 0 to 4 and compare the trees
    trees = {seed: train_scorer(scorer, config, seed) for seed in range(5)}
    texts = {seed: export_text(t, feature_names=columns, show_weights=True) for seed, t in trees.items()}
    print("1. scorer trees identical for seeds 0 to 4:", len(set(texts.values())) == 1)
    print()

    # The tree of seed 0, with the class counts in each leaf of the scorer training set
    tree = trees[0]
    print("2. scorer tree (seed 0). weights = [benign, attack] flows in the scorer split")
    print(texts[0])
    print("feature importances")
    print(pd.Series(tree.feature_importances_, index=columns).round(3).to_string())
    print()

    # Suspicion of every test flow, and the keep probability at two budgets
    s = suspicion_scores(tree, test, config)
    keep1, c1 = keep_probabilities(s, 0.01, floor)
    keep5, c5 = keep_probabilities(s, 0.05, floor)
    print("3. factor c: 1% budget", round(c1, 3), "| 5% budget", round(c5, 3))

    # Check: this gives the same mask as attack_aware_mask
    same = np.array_equal(attack_aware_mask(s, 0.05, 0, floor), np.random.default_rng(0).random(len(s)) < keep5)
    print("   same mask as attack_aware_mask (seed 0, 5%):", same)
    print()

    # Per class: suspicion, keep probability, and the observed recall from the saved results
    table = pd.DataFrame({"attack": test["Attack"].to_numpy(), "s": s, "k1": keep1, "k5": keep5})
    g = table.groupby("attack")
    out = pd.DataFrame({
        "flows": g.size(),
        "mean_suspicion": g["s"].mean(),
        "share_suspicion>=0.5": (table["s"] >= 0.5).groupby(table["attack"]).mean(),
        "mean_keep@1%": g["k1"].mean(),
        "mean_keep@5%": g["k5"].mean(),
    })

    raw = pd.read_csv(R / "regime1_raw.csv")
    rf = raw[(raw["run"] == "main") & (raw["model"] == "random_forest") & (raw["policy"] == "attack_aware")]
    classes = [c for c in out.index if c != "Benign"]
    observed = rf[rf["budget"] == 0.05][["recall_" + c for c in classes]].mean()
    full = rf[rf["budget"] == 1.0][["recall_" + c for c in classes]].mean()
    observed.index = classes
    full.index = classes
    out["recall_no_sampling"] = full
    out["expected_recall@5%"] = out["mean_keep@5%"] * out["recall_no_sampling"]
    out["observed_recall@5%"] = observed
    print("4. per class (test set, seed 0 scorer). expected = mean keep probability x recall without sampling")
    print(out.round(4).to_string())
    print()

    # Per leaf: how many test flows of each class fall into each leaf of the scorer tree
    leaves = tree.apply(test[columns])
    print("5. test flows per class (rows) and scorer leaf (columns)")
    print(pd.crosstab(test["Attack"], leaves).to_string())
    leaf = pd.DataFrame({"s": s, "k5": keep5, "attack": test["Label"].to_numpy()}).groupby(leaves)
    summary = pd.DataFrame({
        "flows": leaf.size(),
        "attack_share": leaf["attack"].mean(),
        "suspicion": leaf["s"].mean(),
        "keep@5%": leaf["k5"].mean(),
    })
    print()
    print("6. per leaf")
    print(summary.round(4).to_string())


if __name__ == "__main__":
    main()
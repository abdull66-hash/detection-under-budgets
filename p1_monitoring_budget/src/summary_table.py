"""Summary table for the report (random forest, TTL dropped, regime i)."""

import pandas as pd

from common.io import REPO_ROOT, save_csv
from p1_monitoring_budget.src.preprocess import load_clean_data, load_config, split_data

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Policies in the order of the table, with the names shown in the report
NAMES = {
    "uniform": "uniform",
    "stratified": "stratified",
    "attack_aware": "attack-aware (uses labels)",
    "host_keyed": "host-keyed*",
}


def fmt(mean, low, high):
    # Text like 0.095 [0.093, 0.097]
    return f"{mean:.3f} [{low:.3f}, {high:.3f}]"


def with_interval(policy, budget, metric, summary, spread):
    # Host-keyed: mean and the 2.5% to 97.5% range over 100 hash seeds
    if policy == "host_keyed":
        values = spread[spread["budget"] == budget][metric]
        return fmt(values.mean(), values.quantile(0.025), values.quantile(0.975))

    # The others: mean and 95% bootstrap interval over 5 seeds
    row = summary[(summary["policy"] == policy) & (summary["budget"] == budget)].iloc[0]
    return fmt(row[metric], row[metric + "_low"], row[metric + "_high"])


def main():
    # Random forest, TTL dropped, regime (i): 5 seeds
    summary = pd.read_csv(RESULTS_DIR / "results_summary.csv")
    summary = summary[
        (summary["regime"] == 1) & (summary["run"] == "main") & (summary["model"] == "random_forest")
    ]

    # Host-keyed with 100 hash seeds
    spread = pd.read_csv(RESULTS_DIR / "hostkeyed_spread.csv")

    # Smallest budget with 90% campaign detection
    minimum = pd.read_csv(RESULTS_DIR / "min_budget_90.csv")
    minimum = minimum[
        (minimum["regime"] == 1) & (minimum["run"] == "main") & (minimum["model"] == "random_forest")
    ]

    # False alarms and precision at a 5% budget (5-seed means)
    raw = pd.read_csv(RESULTS_DIR / "regime1_raw.csv")
    raw = raw[(raw["run"] == "main") & (raw["model"] == "random_forest") & (raw["budget"] == 0.05)]
    mean = raw.groupby("policy")[["recall", "fpr"]].mean()

    # Number of attack and benign flows in the test set
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    n_attack = int(test["Label"].sum())
    n_benign = len(test) - n_attack

    rows = []
    for policy, name in NAMES.items():
        smallest = minimum[minimum["policy"] == policy].set_index("definition")["min_budget_90"]
        true_alerts = mean.loc[policy, "recall"] * n_attack
        false_alerts = mean.loc[policy, "fpr"] * n_benign
        rows.append({
            "policy": name,
            "smallest budget, 90% campaigns (primary)": smallest["primary"],
            "smallest budget, 90% campaigns (coarse)": smallest["coarse"],
            "recall at 1%": with_interval(policy, 0.01, "recall", summary, spread),
            "recall at 5%": with_interval(policy, 0.05, "recall", summary, spread),
            "campaigns detected at 1%": with_interval(policy, 0.01, "campaign_primary", summary, spread),
            "campaigns detected at 5%": with_interval(policy, 0.05, "campaign_primary", summary, spread),
            "false alarms per 100k benign at 5%": round(mean.loc[policy, "fpr"] * 100_000, 1),
            "precision at 5%": round(true_alerts / (true_alerts + false_alerts), 3),
        })
    table = pd.DataFrame(rows)
    save_csv(table, RESULTS_DIR / "summary_table.csv")

    # Print as a table that can be pasted into the report
    header = list(table.columns)
    print("| " + " | ".join(header) + " |")
    print("|" + "---|" * len(header))
    for _, r in table.iterrows():
        print("| " + " | ".join(str(r[c]) for c in header) + " |")


if __name__ == "__main__":
    main()
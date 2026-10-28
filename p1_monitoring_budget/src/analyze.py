"""Make tables from the raw result files."""

import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.metrics import bootstrap_ci

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Metrics shown in the table
METRICS = ["recall", "fpr", "pr_auc", "macro_f1"]


def baseline_table():
    # Read the raw baseline results (one row per model and seed)
    raw = pd.read_csv(RESULTS_DIR / "baseline_raw.csv")

    rows = []
    for (run, model), group in raw.groupby(["run", "model"]):
        row = {"run": run, "model": model, "seeds": len(group)}

        # Mean and 95% bootstrap interval over the seeds
        for metric in METRICS:
            mean, low, high = bootstrap_ci(group[metric])
            row[metric] = f"{mean:.4f} [{low:.4f}, {high:.4f}]"

        # Average training time in seconds
        row["fit_seconds"] = round(group["fit_seconds"].mean(), 1)
        rows.append(row)
    return pd.DataFrame(rows)

def regime1_table():
    # Read the raw regime (i) results (one row per model, seed, policy and budget)
    raw = pd.read_csv(RESULTS_DIR / "regime1_raw.csv")

    # Main run only (TTL dropped)
    raw = raw[raw["run"] == "main"]

    rows = []
    for (model, policy, budget), group in raw.groupby(["model", "policy", "budget"]):
        # Mean recall and 95% bootstrap interval over the 5 seeds
        mean, low, high = bootstrap_ci(group["recall"])
        rows.append({
            "model": model,
            "policy": policy,
            "budget": budget,
            "recall": round(mean, 4),
            "recall_low": round(low, 4),
            "recall_high": round(high, 4),
            "fpr": round(group["fpr"].mean(), 5),
            "realized_rate": round(group["realized_rate"].mean(), 5),
            "attack_visible": round(group["attack_visible"].mean(), 4),
        })
    table = pd.DataFrame(rows)

    # Recall with no sampling (budget 1.0), one value for each model
    full = table[table["budget"] == 1.0].groupby("model")["recall"].mean()

    # Expected recall for uniform sampling = budget x recall with no sampling
    table["expected_uniform"] = (table["budget"] * table["model"].map(full)).round(4)
    return table

def plot_regime1():
    # Draw recall against budget for random forest, one line per policy
    import matplotlib.pyplot as plt

    from common.plotting import save_figure, set_style

    set_style()
    table = pd.read_csv(RESULTS_DIR / "regime1_table.csv")
    rf = table[table["model"] == "random_forest"]

    fig, ax = plt.subplots(figsize=(6.5, 4.5))
    for policy, marker in [("uniform", "o"), ("stratified", "s"), ("host_keyed", "^")]:
        part = rf[rf["policy"] == policy].sort_values("budget")
        # Error bars: distance from the mean to the 95% interval
        below = (part["recall"] - part["recall_low"]).clip(lower=0)
        above = (part["recall_high"] - part["recall"]).clip(lower=0)
        ax.errorbar(part["budget"], part["recall"], yerr=[below, above],
                    marker=marker, capsize=3, label=policy)

    # Dashed line: recall equal to the budget
    ax.plot([0.001, 1], [0.001, 1], linestyle="--", color="gray", label="recall = budget")

    # Log scale for the budget; symlog on recall so that 0 can be shown
    ax.set_xscale("log")
    ax.set_yscale("symlog", linthresh=1e-4)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel("Budget (share of flows kept)")
    ax.set_ylabel("Attack recall (flow level)")
    ax.set_title("Random forest, TTL dropped, trained on full data")
    ax.legend()

    # Save as PNG and PDF
    save_figure(fig, RESULTS_DIR / "regime1_recall_vs_budget")

if __name__ == "__main__":
    # Baseline table
    save_csv(baseline_table(), RESULTS_DIR / "baseline_table.csv")

    # Regime (i) table
    table = regime1_table()
    save_csv(table, RESULTS_DIR / "regime1_table.csv")

    # Show random forest for each policy
    rf = table[table["model"] == "random_forest"]
    columns = ["budget", "recall", "recall_low", "recall_high", "expected_uniform", "realized_rate", "attack_visible"]
    for policy in ["uniform", "stratified", "host_keyed"]:
        print(policy)
        print(rf[rf["policy"] == policy][columns].to_string(index=False))
        print()
        plot_regime1()
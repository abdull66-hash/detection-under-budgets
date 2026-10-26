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


if __name__ == "__main__":
    table = baseline_table()
    print(table.to_string(index=False))
    save_csv(table, RESULTS_DIR / "baseline_table.csv")
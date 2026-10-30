"""Tables for regime (i) and regime (ii), with 95% intervals."""

import numpy as np
import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.metrics import bootstrap_ci
from p1_monitoring_budget.src.campaigns import make_campaign_ids
from p1_monitoring_budget.src.preprocess import load_clean_data, load_config, split_data

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Metrics shown with a mean and an interval
METRICS = ["recall", "fpr", "pr_auc", "macro_f1", "campaign_primary", "campaign_coarse"]


def load_all():
    # Regime (i): every row
    one = pd.read_csv(RESULTS_DIR / "regime1_raw.csv")
    one["regime"] = 1
    one["trained"] = True

    # Regime (ii): main run only
    two = pd.read_csv(RESULTS_DIR / "regime2_raw.csv")
    return pd.concat([one, two], ignore_index=True)


def summary(rows):
    # PR-AUC has no meaning where no model was trained
    rows = rows.copy()
    trained = rows["trained"].astype(bool)
    rows.loc[~trained, "pr_auc"] = np.nan

    keys = ["regime", "run", "model", "policy", "budget"]
    out = []
    for key, group in rows.groupby(keys):
        row = dict(zip(keys, key))
        row["seeds"] = len(group)

        # Mean and 95% bootstrap interval over the seeds
        for metric in METRICS:
            values = group[metric].dropna()
            if len(values) == 0:
                mean, low, high = np.nan, np.nan, np.nan
            else:
                mean, low, high = bootstrap_ci(values)
            row[metric] = round(mean, 4)
            row[metric + "_low"] = round(low, 4)
            row[metric + "_high"] = round(high, 4)

        # Plain means for the ceilings and the realized rate
        row["realized_rate"] = round(group["realized_rate"].mean(), 5)
        row["attack_visible"] = round(group["attack_visible"].mean(), 4)
        row["campaigns_visible_primary"] = round(group["campaigns_visible_primary"].mean(), 4)
        out.append(row)
    return pd.DataFrame(out)


def min_budget(table, level=0.9):
    keys = ["regime", "run", "model", "policy"]
    out = []
    for key, group in table.groupby(keys):
        # Start at the largest budget and go down
        group = group.sort_values("budget", ascending=False)
        for metric in ["campaign_primary", "campaign_coarse"]:
            found, realized = np.nan, np.nan
            for _, r in group.iterrows():
                # Stop at the first budget that is below the level
                if r[metric] >= level:
                    found, realized = r["budget"], r["realized_rate"]
                else:
                    break
            row = dict(zip(keys, key))
            row["definition"] = metric.replace("campaign_", "")
            row["min_budget_90"] = found
            row["realized_rate_there"] = realized
            out.append(row)
    return pd.DataFrame(out)


def uniform_check(table):
    # Campaign sizes in the test set
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    cc = config["campaigns"]

    # Uniform sampling, random forest, regime (i), main run
    part = table[
        (table["regime"] == 1) & (table["run"] == "main")
        & (table["model"] == "random_forest") & (table["policy"] == "uniform")
    ].sort_values("budget")

    # Share of attack flows the model flags when nothing is sampled
    flag_rate = float(part[part["budget"] == 1.0]["recall"].iloc[0])

    out = []
    for name, columns in [("primary", cc["primary_columns"]), ("coarse", cc["coarse_columns"])]:
        ids, k = make_campaign_ids(test, columns, cc["min_flows"])
        sizes = np.bincount(ids[ids >= 0])
        for _, r in part.iterrows():
            p = r["budget"]
            # A campaign is detected if at least one of its flows is sampled and flagged
            expected = float(np.mean(1 - (1 - p * flag_rate) ** sizes))
            out.append({
                "definition": name,
                "budget": p,
                "observed": r["campaign_" + name],
                "expected": round(expected, 4),
            })
    return pd.DataFrame(out)


if __name__ == "__main__":
    table = summary(load_all())
    save_csv(table, RESULTS_DIR / "results_summary.csv")

    minimum = min_budget(table)
    save_csv(minimum, RESULTS_DIR / "min_budget_90.csv")

    check = uniform_check(table)
    save_csv(check, RESULTS_DIR / "uniform_check.csv")

    # Show random forest, main run
    rf = table[(table["model"] == "random_forest") & (table["run"] == "main")]
    for metric in ["recall", "campaign_primary", "fpr"]:
        print(metric)
        print(rf.pivot_table(index=["regime", "policy"], columns="budget", values=metric).round(4).to_string())
        print()

    print("smallest budget with 90% campaign detection (random forest, main run)")
    shown = minimum[(minimum["model"] == "random_forest") & (minimum["run"] == "main")]
    print(shown.to_string(index=False))
    print()

    print("uniform sampling: observed and expected campaign detection")
    print(check.to_string(index=False))
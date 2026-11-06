"""Print the key result tables so they can be read and checked. Writes nothing."""

from datetime import datetime

import pandas as pd

from common.io import REPO_ROOT
from p1_monitoring_budget.src.preprocess import load_clean_data, load_config

# Folder with the saved results
R = REPO_ROOT / "p1_monitoring_budget" / "results"

POLICIES = ["uniform", "stratified", "attack_aware", "host_keyed"]


def show(title, table):
    # Print a title and a table
    print(title)
    print(table.to_string())
    print()


def table_a(one):
    # All three models, main run, regime (i): 5-seed means
    data = one[one["run"] == "main"]
    mean = data.groupby(["model", "policy", "budget"])[["recall", "campaign_primary", "fpr"]].mean()
    rows = []
    for model in ["logreg", "random_forest", "lightgbm"]:
        for policy in POLICIES:
            row = {"model": model, "policy": policy}
            for b in [0.01, 0.05]:
                row[f"recall@{b}"] = round(mean.loc[(model, policy, b), "recall"], 4)
                row[f"campaigns@{b}"] = round(mean.loc[(model, policy, b), "campaign_primary"], 4)
            row["false_alarms_per_100k@0.05"] = round(mean.loc[(model, policy, 0.05), "fpr"] * 1e5, 1)
            rows.append(row)
    show("A. all models, main run, regime (i), 5-seed means", pd.DataFrame(rows).set_index(["model", "policy"]))


def table_b(one):
    # TTL dropped (main) and TTL kept (sensitivity), random forest, regime (i)
    data = one[one["model"] == "random_forest"]
    rows = []
    for policy in POLICIES:
        row = {"policy": policy}
        for run in ["main", "sensitivity"]:
            part = data[(data["run"] == run) & (data["policy"] == policy)]
            mean = part.groupby("budget")[["recall", "campaign_primary", "fpr"]].mean()
            row[f"recall@0.05 {run}"] = round(mean.loc[0.05, "recall"], 4)
            row[f"campaigns@0.01 {run}"] = round(mean.loc[0.01, "campaign_primary"], 4)
            row[f"false_alarms_per_100k@0.05 {run}"] = round(mean.loc[0.05, "fpr"] * 1e5, 1)
        rows.append(row)
    show("B. TTL dropped (main) and TTL kept (sensitivity), random forest, regime (i)", pd.DataFrame(rows).set_index("policy"))


def table_c(one):
    # Recall for each attack class, random forest, main run, regime (i)
    data = one[(one["run"] == "main") & (one["model"] == "random_forest")]
    classes = [c for c in data.columns if c.startswith("recall_")]

    def class_recall(policy, budget):
        part = data[(data["policy"] == policy) & (data["budget"] == budget)]
        return part[classes].mean()

    table = pd.DataFrame({
        "budget 1.0": class_recall("uniform", 1.0),
        "uniform 0.05": class_recall("uniform", 0.05),
        "attack_aware 0.05": class_recall("attack_aware", 0.05),
    }).round(4)
    table.index = [name.replace("recall_", "") for name in table.index]
    show("C. recall per attack class, random forest, main run, regime (i)", table)


def table_d(one, two):
    # The two lowest budgets, random forest, main run, both regimes
    rows = []
    for regime, data in [(1, one), (2, two)]:
        part = data[(data["run"] == "main") & (data["model"] == "random_forest") & data["budget"].isin([0.001, 0.01])]
        g = part.groupby(["policy", "budget"])[["n_sampled", "recall", "fpr"]].mean().reset_index()
        g["regime"] = regime
        g["n_sampled"] = g["n_sampled"].round(0)
        g["recall"] = g["recall"].round(4)
        g["false_alarms_per_100k"] = (g["fpr"] * 1e5).round(2)
        rows.append(g[["regime", "policy", "budget", "n_sampled", "recall", "false_alarms_per_100k"]])
    show("D. lowest budgets, random forest, main run", pd.concat(rows).set_index(["regime", "policy", "budget"]))


def table_e(one):
    # Share of coarse campaigns detected, random forest, main run, regime (i)
    data = one[(one["run"] == "main") & (one["model"] == "random_forest")]
    table = data.groupby(["policy", "budget"])["campaign_coarse"].mean().unstack().round(4)
    show("E. coarse campaigns detected, random forest, main run, regime (i)", table)


def table_f():
    # Flows with a duration above 0 ms, by class
    df = load_clean_data(load_config())
    nonzero = df[df["FLOW_DURATION_MILLISECONDS"] > 0]
    table = nonzero.groupby("Attack")["FLOW_DURATION_MILLISECONDS"].agg(["size", "min", "median", "max"])
    show("F. flows with duration above 0 ms", table)


def list_files():
    # Files in the results folder, oldest first
    print("G. files in results (oldest first)")
    for p in sorted(R.glob("*"), key=lambda p: p.stat().st_mtime):
        print(datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M"), p.stat().st_size, p.name)


def main():
    one = pd.read_csv(R / "regime1_raw.csv")
    two = pd.read_csv(R / "regime2_raw.csv")
    table_a(one)
    table_b(one)
    table_c(one)
    table_d(one, two)
    table_e(one)
    table_f()
    list_files()


if __name__ == "__main__":
    main()
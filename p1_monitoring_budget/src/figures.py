"""Figures for the report. Each figure also prints the numbers it plots."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common.io import REPO_ROOT
from common.plotting import save_figure, set_style
from p1_monitoring_budget.src.preprocess import load_clean_data, load_config, split_data

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Color and marker for each policy (the same in every figure)
STYLE = {
    "uniform": ("tab:blue", "o"),
    "stratified": ("tab:green", "s"),
    "attack_aware": ("tab:red", "D"),
    "host_keyed": ("tab:orange", "^"),
}
LABELS = {
    "uniform": "uniform",
    "stratified": "stratified",
    "attack_aware": "attack-aware (uses labels)",
    "host_keyed": "host-keyed (100 hash seeds)",
}


def load_rf():
    # Random forest, main run (TTL dropped), regime (i)
    t = pd.read_csv(RESULTS_DIR / "results_summary.csv")
    return t[(t["regime"] == 1) & (t["run"] == "main") & (t["model"] == "random_forest")]


def host_keyed_band(metric):
    # Mean and the 2.5% and 97.5% percentiles over the 100 hash seeds
    s = pd.read_csv(RESULTS_DIR / "hostkeyed_spread.csv")
    g = s.groupby("budget")[metric]
    band = pd.DataFrame({"mean": g.mean(), "low": g.quantile(0.025), "high": g.quantile(0.975)})
    return band.reset_index()


def draw_policies(ax, rf, metric):
    # Remember every plotted number, so it can be printed
    plotted = []

    # Three policies with 5 seeds: mean and 95% interval
    for policy in ["uniform", "stratified", "attack_aware"]:
        color, marker = STYLE[policy]
        part = rf[rf["policy"] == policy].sort_values("budget")
        below = (part[metric] - part[metric + "_low"]).clip(lower=0)
        above = (part[metric + "_high"] - part[metric]).clip(lower=0)
        ax.errorbar(part["budget"], part[metric], yerr=[below, above],
                    color=color, marker=marker, capsize=3, label=LABELS[policy])
        for _, r in part.iterrows():
            plotted.append({"policy": policy, "budget": r["budget"], "mean": r[metric],
                            "low": r[metric + "_low"], "high": r[metric + "_high"]})

    # Host-keyed: mean and a band between the 2.5% and 97.5% percentiles
    band = host_keyed_band(metric)
    color, marker = STYLE["host_keyed"]
    ax.plot(band["budget"], band["mean"], color=color, marker=marker, label=LABELS["host_keyed"])
    ax.fill_between(band["budget"], band["low"], band["high"], color=color, alpha=0.2)
    for _, r in band.iterrows():
        plotted.append({"policy": "host_keyed", "budget": r["budget"], "mean": r["mean"],
                        "low": r["low"], "high": r["high"]})
    return pd.DataFrame(plotted)


def print_plotted(title, plotted):
    # Print the plotted numbers: one line per policy and budget
    print(title)
    print(plotted.round(4).to_string(index=False))
    print()


def legend_outside(ax):
    # Put the legend to the right of the plot so it hides nothing
    ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)


def figure_recall():
    set_style()
    rf = load_rf()
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    plotted = draw_policies(ax, rf, "recall")

    # Dashed line: recall equal to the budget
    ax.plot([0.001, 1], [0.001, 1], linestyle="--", color="gray", label="recall = budget")

    # Log scale for the budget. Symlog for recall so that 0 can be shown.
    ax.set_xscale("log")
    ax.set_yscale("symlog", linthresh=1e-4)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 1e-4, 1e-3, 1e-2, 0.1, 1])
    ax.set_yticklabels(["0", "0.0001", "0.001", "0.01", "0.1", "1"])
    ax.set_xlabel("Budget (share of flows kept, log scale)")
    ax.set_ylabel("Attack recall (flow level, symlog scale)")
    ax.set_title("Flow-level recall vs budget (random forest, regime i)")
    legend_outside(ax)
    save_figure(fig, RESULTS_DIR / "fig1_recall_vs_budget")
    plt.close(fig)
    print_plotted("Figure 1: recall (mean, low, high)", plotted)


def figure_campaign():
    set_style()
    rf = load_rf()
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    plotted = draw_policies(ax, rf, "campaign_primary")

    # Dotted line: expected value for uniform sampling from the campaign sizes
    check = pd.read_csv(RESULTS_DIR / "uniform_check.csv")
    check = check[check["definition"] == "primary"].sort_values("budget")
    ax.plot(check["budget"], check["expected"], linestyle=":", color="black", label="uniform, formula")

    # Line at 90%
    ax.axhline(0.9, linestyle="--", color="gray", label="90%")

    ax.set_xscale("log")
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Budget (share of flows kept, log scale)")
    ax.set_ylabel("Campaigns detected (share, primary definition)")
    ax.set_title("Campaign-level detection vs budget (random forest, regime i)")
    legend_outside(ax)
    save_figure(fig, RESULTS_DIR / "fig2_campaign_vs_budget")
    plt.close(fig)
    print_plotted("Figure 2: primary campaigns detected (mean, low, high)", plotted)
    print("Figure 2: formula line for uniform sampling")
    print(check[["budget", "expected"]].to_string(index=False))
    print()


def figure_tradeoff():
    set_style()

    # Random forest, main run, regime (i): mean over the 5 seeds, not rounded
    raw = pd.read_csv(RESULTS_DIR / "regime1_raw.csv")
    raw = raw[(raw["run"] == "main") & (raw["model"] == "random_forest")]
    mean = raw.groupby(["policy", "budget"])[["recall", "fpr"]].mean().reset_index()

    # Number of attack and benign flows in the test set
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    n_attack = int(test["Label"].sum())
    n_benign = len(test) - n_attack

    # Precision of the flagged flows: true alerts out of all alerts
    true_alerts = mean["recall"] * n_attack
    false_alerts = mean["fpr"] * n_benign
    mean["precision"] = true_alerts / (true_alerts + false_alerts)

    # Draw one line per policy. Each point is one budget.
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    labels = {"uniform": "uniform", "stratified": "stratified",
              "attack_aware": "attack-aware (uses labels)", "host_keyed": "host-keyed (5 seeds)"}
    for policy in ["uniform", "stratified", "attack_aware", "host_keyed"]:
        color, marker = STYLE[policy]
        # A log scale cannot show zero, so those points are left out
        part = mean[(mean["policy"] == policy) & (mean["recall"] > 0) & (mean["fpr"] > 0)]
        part = part.sort_values("budget")
        ax.plot(part["fpr"], part["recall"], color=color, marker=marker, label=labels[policy])

    # Dashed line: the trade-off of the full model (budget 1.0), extended to low values
    full = mean[(mean["policy"] == "uniform") & (mean["budget"] == 1.0)].iloc[0]
    ratio = full["recall"] / full["fpr"]
    xs = np.array([mean.loc[mean["fpr"] > 0, "fpr"].min(), full["fpr"]])
    ax.plot(xs, ratio * xs, linestyle="--", color="gray", label="same trade-off as the full model")

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("False positive rate (share of benign flows flagged, log scale)")
    ax.set_ylabel("Attack recall (flow level, log scale)")
    ax.set_title("Recall vs false positive rate (random forest, regime i)")
    legend_outside(ax)
    save_figure(fig, RESULTS_DIR / "fig3_recall_vs_fpr")
    plt.close(fig)

    # Print every point of the table behind the figure
    points = mean.sort_values(["policy", "budget"]).copy()
    points["false_alarms_per_100k"] = (points["fpr"] * 100_000).round(2)
    print("Figure 3: points (5-seed means). Points with recall 0 or no false alarms are not drawn.")
    print(points[["policy", "budget", "false_alarms_per_100k", "recall", "precision"]].round(4).to_string(index=False))
    print()


if __name__ == "__main__":
    figure_recall()
    figure_campaign()
    figure_tradeoff()
    print("Saved fig1, fig2 and fig3")
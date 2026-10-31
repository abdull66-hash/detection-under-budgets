"""Figures for the report."""

import matplotlib.pyplot as plt
import pandas as pd

from common.io import REPO_ROOT
from common.plotting import save_figure, set_style

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Color and marker for each policy
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
    # Three policies with 5 seeds: mean and 95% interval
    for policy in ["uniform", "stratified", "attack_aware"]:
        color, marker = STYLE[policy]
        part = rf[rf["policy"] == policy].sort_values("budget")
        below = (part[metric] - part[metric + "_low"]).clip(lower=0)
        above = (part[metric + "_high"] - part[metric]).clip(lower=0)
        ax.errorbar(part["budget"], part[metric], yerr=[below, above],
                    color=color, marker=marker, capsize=3, label=LABELS[policy])

    # Host-keyed: mean and a band between the 2.5% and 97.5% percentiles
    band = host_keyed_band(metric)
    color, marker = STYLE["host_keyed"]
    ax.plot(band["budget"], band["mean"], color=color, marker=marker, label=LABELS["host_keyed"])
    ax.fill_between(band["budget"], band["low"], band["high"], color=color, alpha=0.2)


def figure_recall():
    set_style()
    rf = load_rf()
    fig, ax = plt.subplots(figsize=(7, 4.8))
    draw_policies(ax, rf, "recall")

    # Dashed line: recall equal to the budget
    ax.plot([0.001, 1], [0.001, 1], linestyle="--", color="gray", label="recall = budget")

    # Log scale for the budget. Symlog for recall so that 0 can be shown.
    ax.set_xscale("log")
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.set_ylim(0, 1.2)
    ax.set_yticks([0, 0.001, 0.01, 0.1, 1])
    ax.set_yticklabels(["0", "0.001", "0.01", "0.1", "1"])
    ax.set_xlabel("Budget (share of flows kept, log scale)")
    ax.set_ylabel("Attack recall (flow level, symlog scale)")
    ax.set_title("Flow-level recall vs budget (random forest, regime i)")
    ax.legend(fontsize=8)
    save_figure(fig, RESULTS_DIR / "fig1_recall_vs_budget")
    plt.close(fig)


def figure_campaign():
    set_style()
    rf = load_rf()
    fig, ax = plt.subplots(figsize=(7, 4.8))
    draw_policies(ax, rf, "campaign_primary")

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
    ax.legend(fontsize=8)
    save_figure(fig, RESULTS_DIR / "fig2_campaign_vs_budget")
    plt.close(fig)


if __name__ == "__main__":
    figure_recall()
    figure_campaign()
    print("Saved fig1_recall_vs_budget and fig2_campaign_vs_budget")
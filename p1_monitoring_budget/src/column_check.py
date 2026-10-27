"""Remove each checked column from the main run and compare the results."""

import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.seed import set_all_seeds
from p1_monitoring_budget.src.baseline import score_model
from p1_monitoring_budget.src.models import build_model
from p1_monitoring_budget.src.preprocess import (
    get_feature_columns,
    load_clean_data,
    load_config,
    split_data,
)

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Models to test (logistic regression is skipped because it is slow)
MODELS = ["random_forest", "lightgbm"]


def run_check():
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)

    # The main feature set is the starting point
    main_cols = get_feature_columns(df, config, "main")
    to_check = config["checked_and_kept"]

    # One variant without each column, and one without both
    variants = {}
    for col in to_check:
        variants["without_" + col] = [c for c in main_cols if c != col]
    variants["without_both"] = [c for c in main_cols if c not in to_check]

    rows = []
    for variant, cols in variants.items():
        for name in MODELS:
            for seed in config["seeds"]:
                # Train the model and score it on the test set
                set_all_seeds(seed)
                model = build_model(name, config, seed)
                model.fit(train[cols], train["Label"])
                row = {"variant": variant, "model": name, "seed": seed}
                row.update(score_model(model, test, cols))
                rows.append(row)
                print(variant, name, seed, "recall", round(row["recall"], 4))
    return pd.DataFrame(rows)


def summarize(raw):
    # The main results come from the full baseline run
    base = pd.read_csv(RESULTS_DIR / "baseline_raw.csv")
    base = base[(base["run"] == "main") & (base["model"].isin(MODELS))].copy()
    base["variant"] = "main"
    both = pd.concat([base, raw], ignore_index=True)

    # Mean over the 5 seeds for each variant and model
    metrics = ["recall", "fpr", "pr_auc", "macro_f1"]
    table = both.groupby(["model", "variant"])[metrics].mean().reset_index()

    # Change compared with the main run of the same model
    main = table[table["variant"] == "main"].set_index("model")
    table["d_recall"] = [r["recall"] - main.loc[r["model"], "recall"] for _, r in table.iterrows()]
    table["d_pr_auc"] = [r["pr_auc"] - main.loc[r["model"], "pr_auc"] for _, r in table.iterrows()]
    return table.round(4)


if __name__ == "__main__":
    raw = run_check()
    save_csv(raw, RESULTS_DIR / "column_check_raw.csv")
    table = summarize(raw)
    print(table.to_string(index=False))
    save_csv(table, RESULTS_DIR / "column_check_table.csv")
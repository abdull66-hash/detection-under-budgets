"""Host-keyed sampling with many hash seeds (regime i, one random forest)."""

import hashlib

import numpy as np
import pandas as pd

from common.io import REPO_ROOT, save_csv
from common.seed import set_all_seeds
from p1_monitoring_budget.src.campaigns import campaign_detection, make_campaign_ids
from p1_monitoring_budget.src.models import build_model
from p1_monitoring_budget.src.preprocess import (
    get_feature_columns,
    load_clean_data,
    load_config,
    split_data,
)
from p1_monitoring_budget.src.sampling import host_keyed_mask

# Folder for the result files
RESULTS_DIR = REPO_ROOT / "p1_monitoring_budget" / "results"

# Number of different hash seeds
N_SEEDS = 100


def main():
    # Load the settings and the data, then split
    config = load_config()
    df = load_clean_data(config)
    train, scorer, test = split_data(df, config)
    cols = get_feature_columns(df, config, "main")

    # Train one random forest on the full training set and score the test set once
    set_all_seeds(0)
    model = build_model("random_forest", config, 0)
    model.fit(train[cols], train["Label"])
    flagged_all = model.predict_proba(test[cols])[:, 1] >= 0.5
    print("model trained")

    # Test labels and primary campaigns
    y_true = test["Label"].to_numpy()
    cc = config["campaigns"]
    ids, k = make_campaign_ids(test, cc["primary_columns"], cc["min_flows"])

    # Host pair of every test flow, built once
    key_cols = config["sampling"]["host_key_columns"]
    keys = test[key_cols[0]].astype(str)
    for col in key_cols[1:]:
        keys = keys + "|" + test[col].astype(str)
    codes, unique_keys = pd.factorize(keys)
    print("host pairs in the test set:", len(unique_keys))

    def numbers_for(seed):
        # A number between 0 and 1 for every host pair (same formula as host_keyed_mask)
        out = np.empty(len(unique_keys))
        for i, key in enumerate(unique_keys):
            digest = hashlib.blake2b(f"{seed}|{key}".encode(), digest_size=8).digest()
            out[i] = int.from_bytes(digest, "big") / 2**64
        return out

    # Check: this shortcut gives the same mask as host_keyed_mask
    shortcut = numbers_for(0)[codes] < 0.1
    assert np.array_equal(shortcut, host_keyed_mask(test, 0.1, 0, key_cols))
    print("check passed: same mask as host_keyed_mask")

    rows = []
    for seed in range(N_SEEDS):
        numbers = numbers_for(seed)[codes]
        for budget in config["budgets"]:
            mask = numbers < budget
            flagged = flagged_all & mask
            rows.append({
                "hash_seed": seed,
                "budget": budget,
                "realized_rate": float(mask.mean()),
                "recall": float(flagged[y_true == 1].mean()),
                "campaign_primary": campaign_detection(ids, k, flagged),
            })
    result = pd.DataFrame(rows)
    save_csv(result, RESULTS_DIR / "hostkeyed_spread.csv")

    # Summary per budget
    summary = []
    for budget, group in result.groupby("budget"):
        summary.append({
            "budget": budget,
            "recall_mean": round(group["recall"].mean(), 4),
            "recall_p2.5": round(group["recall"].quantile(0.025), 4),
            "recall_p97.5": round(group["recall"].quantile(0.975), 4),
            "share_zero_recall": round((group["recall"] == 0).mean(), 2),
            "campaign_mean": round(group["campaign_primary"].mean(), 4),
            "campaign_p2.5": round(group["campaign_primary"].quantile(0.025), 4),
            "campaign_p97.5": round(group["campaign_primary"].quantile(0.975), 4),
            "realized_min": round(group["realized_rate"].min(), 4),
            "realized_max": round(group["realized_rate"].max(), 4),
        })
    print(pd.DataFrame(summary).to_string(index=False))


if __name__ == "__main__":
    main()
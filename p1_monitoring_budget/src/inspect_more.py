"""Print regime (i) and regime (ii) results for all models. Prints only."""

import pandas as pd

from common.io import REPO_ROOT

# Folder with the saved results
R = REPO_ROOT / "p1_monitoring_budget" / "results"

# Main run only. Regime (ii) has no other run.
one = pd.read_csv(R / "regime1_raw.csv")
one = one[one["run"] == "main"].assign(regime=1)
two = pd.read_csv(R / "regime2_raw.csv").assign(regime=2)
both = pd.concat([one, two])
both = both[both["budget"].isin([0.01, 0.05])].copy()
both["false_alarms_per_100k"] = both["fpr"] * 100_000

# One table per metric: rows = model and policy, columns = regime and budget
for metric in ["recall", "campaign_primary", "false_alarms_per_100k"]:
    print(metric)
    print(both.pivot_table(index=["model", "policy"], columns=["regime", "budget"], values=metric).round(4).to_string())
    print()
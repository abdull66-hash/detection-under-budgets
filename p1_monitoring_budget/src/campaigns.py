"""Build attack campaigns and measure campaign-level detection."""

import numpy as np


def make_campaign_ids(test, columns, min_flows):
    # Every flow starts with campaign number -1 (no campaign)
    ids = np.full(len(test), -1, dtype=int)

    # Look only at attack flows
    is_attack = (test["Label"] == 1).to_numpy()
    attacks = test[is_attack]

    # Give each campaign (same values in the key columns) a number
    group_number = attacks.groupby(columns, sort=True).ngroup().to_numpy()

    # Keep only campaigns with enough flows
    sizes = np.bincount(group_number)
    keep = sizes >= min_flows

    # Number the kept campaigns 0, 1, 2, ...
    new_number = np.cumsum(keep) - 1
    valid = keep[group_number]

    # Write the campaign number into the flows that belong to a kept campaign
    positions = np.flatnonzero(is_attack)
    ids[positions[valid]] = new_number[group_number[valid]]
    return ids, int(keep.sum())


def campaign_detection(ids, n_campaigns, detected_flows):
    # No campaigns means nothing to measure
    if n_campaigns == 0:
        return float("nan")

    # Campaigns that have at least one detected flow
    hit = ids[(ids >= 0) & detected_flows]
    return len(np.unique(hit)) / n_campaigns
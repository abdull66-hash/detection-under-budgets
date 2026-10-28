"""Sampling policies. Each one returns a True/False list: True = the flow is kept."""

import hashlib

import numpy as np
import pandas as pd


def uniform_mask(n_flows, budget, seed):
    # Keep each flow with probability = budget
    rng = np.random.default_rng(seed)
    return rng.random(n_flows) < budget


def host_keyed_mask(df, budget, seed, key_columns):
    # Join the key columns into one text key per flow, like "ip1|ip2"
    keys = df[key_columns[0]].astype(str)
    for col in key_columns[1:]:
        keys = keys + "|" + df[col].astype(str)

    # Give each different key a number between 0 and 1 (same key, same number)
    numbers = {}
    for key in keys.unique():
        digest = hashlib.blake2b(f"{seed}|{key}".encode(), digest_size=8).digest()
        numbers[key] = int.from_bytes(digest, "big") / 2**64

    # Keep the flows whose key number is below the budget
    return (keys.map(numbers) < budget).to_numpy()


def make_strata(df):
    # Port class from the destination port
    port = df["L4_DST_PORT"]
    port_class = np.where(port < 1024, "well_known", np.where(port < 49152, "registered", "dynamic"))

    # Stratum = protocol + port class
    return df["PROTOCOL"].astype(str) + "_" + pd.Series(port_class, index=df.index)


def stratified_mask(df, budget, seed, min_per_stratum):
    rng = np.random.default_rng(seed)
    strata = make_strata(df)
    sizes = strata.value_counts()

    # Total number of flows to keep
    total = int(round(budget * len(df)))

    # Every stratum keeps at least min_per_stratum flows (or all its flows if fewer)
    floor = sizes.clip(upper=min_per_stratum)

    # The rest of the budget is shared in proportion to the size of what is left
    extra = max(total - floor.sum(), 0)
    rest = sizes - floor
    if rest.sum() > 0:
        share = rest / rest.sum() * extra
    else:
        share = rest * 0
    keep_n = (floor + share).round().astype(int).clip(upper=sizes)

    # Pick that many flows at random inside each stratum
    mask = np.zeros(len(df), dtype=bool)
    positions = np.arange(len(df))
    for name, n_keep in keep_n.items():
        inside = positions[(strata == name).to_numpy()]
        mask[rng.choice(inside, size=n_keep, replace=False)] = True
    return mask


def make_mask(policy, df, budget, seed, config):
    # Pick the policy by name
    if policy == "uniform":
        return uniform_mask(len(df), budget, seed)
    if policy == "host_keyed":
        return host_keyed_mask(df, budget, seed, config["sampling"]["host_key_columns"])
    if policy == "stratified":
        return stratified_mask(df, budget, seed, config["sampling"]["min_per_stratum"])
    raise ValueError(f"Unknown policy: {policy}")
"""Tests for the sampling policies."""

import numpy as np
import pandas as pd
import pytest

from p1_monitoring_budget.src.sampling import (
    host_keyed_mask,
    make_mask,
    make_strata,
    stratified_mask,
    uniform_mask,
)

# Same sampling settings as p1.yaml
KEYS = ["IPV4_SRC_ADDR", "IPV4_DST_ADDR"]
CONFIG = {"sampling": {"host_key_columns": KEYS, "min_per_stratum": 1}}


def make_data(n=20000):
    # A small fake table: 2000 host pairs, 3 protocols, 6 ports
    rng = np.random.default_rng(1)
    return pd.DataFrame({
        "IPV4_SRC_ADDR": rng.choice([f"10.0.0.{i}" for i in range(50)], n),
        "IPV4_DST_ADDR": rng.choice([f"10.1.0.{i}" for i in range(40)], n),
        "PROTOCOL": rng.choice([6, 17, 1], n),
        "L4_DST_PORT": rng.choice([22, 53, 80, 443, 5000, 60000], n),
    })


def test_uniform_rate_is_close_to_budget():
    mask = uniform_mask(100000, 0.05, 0)
    assert abs(mask.mean() - 0.05) < 0.005


def test_uniform_is_repeatable():
    # The same seed must give the same flows
    assert np.array_equal(uniform_mask(5000, 0.1, 3), uniform_mask(5000, 0.1, 3))


def test_uniform_seeds_differ():
    # A different seed must give different flows
    assert not np.array_equal(uniform_mask(5000, 0.1, 0), uniform_mask(5000, 0.1, 1))


def test_host_keyed_keeps_whole_pairs():
    df = make_data()
    mask = host_keyed_mask(df, 0.3, 0, KEYS)

    # All flows of one host pair must have the same decision
    check = pd.Series(mask).groupby([df["IPV4_SRC_ADDR"], df["IPV4_DST_ADDR"]]).nunique()
    assert (check == 1).all()


def test_host_keyed_is_repeatable():
    df = make_data()
    first = host_keyed_mask(df, 0.2, 5, KEYS)
    second = host_keyed_mask(df, 0.2, 5, KEYS)
    assert np.array_equal(first, second)


def test_host_keyed_rate_is_close_with_many_pairs():
    # With 2000 pairs the share of kept flows is close to the budget
    df = make_data()
    mask = host_keyed_mask(df, 0.1, 0, KEYS)
    assert abs(mask.mean() - 0.1) < 0.02


def test_stratified_rate_is_close_to_budget():
    df = make_data()
    mask = stratified_mask(df, 0.05, 0, 1)
    assert abs(mask.mean() - 0.05) < 0.005


def test_stratified_keeps_every_stratum():
    df = make_data()
    mask = stratified_mask(df, 0.05, 0, 1)

    # Every stratum must keep at least one flow
    kept = pd.Series(mask).groupby(make_strata(df)).any()
    assert kept.all()


def test_stratified_is_repeatable():
    df = make_data()
    first = stratified_mask(df, 0.05, 2, 1)
    second = stratified_mask(df, 0.05, 2, 1)
    assert np.array_equal(first, second)


def test_full_budget_keeps_everything():
    df = make_data()
    for policy in ["uniform", "host_keyed", "stratified"]:
        assert make_mask(policy, df, 1.0, 0, CONFIG).all()


def test_unknown_policy_raises():
    with pytest.raises(ValueError):
        make_mask("no_such_policy", make_data(), 0.1, 0, CONFIG)
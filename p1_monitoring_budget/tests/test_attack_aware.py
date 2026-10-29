"""Tests for the attack-aware sampler."""

import numpy as np
import pandas as pd

from p1_monitoring_budget.src.sampling import (
    attack_aware_mask,
    suspicion_scores,
    train_scorer,
)

FEATURES = ["PROTOCOL", "L4_DST_PORT", "TCP_FLAGS", "IN_BYTES", "IN_PKTS"]
CONFIG = {"sampling": {"scorer_features": FEATURES, "scorer_depth": 3}}


def make_suspicion(n=50000):
    # 10% of flows look suspicious, the rest do not
    suspicion = np.zeros(n)
    suspicion[: n // 10] = 1.0
    return suspicion


def test_rate_is_close_to_budget():
    mask = attack_aware_mask(make_suspicion(), 0.05, 0, 0.01)
    assert abs(mask.mean() - 0.05) < 0.005


def test_same_seed_gives_same_result():
    first = attack_aware_mask(make_suspicion(), 0.05, 7, 0.01)
    second = attack_aware_mask(make_suspicion(), 0.05, 7, 0.01)
    assert np.array_equal(first, second)


def test_suspicious_flows_are_kept_more_often():
    suspicion = make_suspicion()
    mask = attack_aware_mask(suspicion, 0.05, 0, 0.01)
    assert mask[suspicion == 1].mean() > mask[suspicion == 0].mean()


def test_full_budget_keeps_everything():
    assert attack_aware_mask(make_suspicion(), 1.0, 0, 0.01).all()


def test_no_suspicion_means_uniform_sampling():
    # With the same score for every flow, all flows have the same chance
    mask = attack_aware_mask(np.zeros(50000), 0.05, 0, 0.01)
    assert abs(mask.mean() - 0.05) < 0.005


def test_scorer_reads_only_the_listed_fields():
    # A fake table where the label depends on the destination port
    rng = np.random.default_rng(0)
    df = pd.DataFrame({name: rng.integers(0, 2000, 3000) for name in FEATURES})
    df["Label"] = (df["L4_DST_PORT"] > 1000).astype(int)

    tree = train_scorer(df, CONFIG, 0)
    scores = suspicion_scores(tree, df, CONFIG)

    # The tree reads 5 fields, scores are between 0 and 1, attacks score higher
    assert tree.n_features_in_ == 5
    assert scores.min() >= 0 and scores.max() <= 1
    assert scores[df["Label"] == 1].mean() > scores[df["Label"] == 0].mean()
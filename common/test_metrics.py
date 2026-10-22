"""Small tests that check my metric helpers give the right answers."""

import numpy as np

from common.metrics import bootstrap_ci, recall_score_binary, false_positive_rate


def test_recall_simple_case():
    # I have 4 real attacks and I catch 3 of them
    y_true = [1, 1, 1, 1, 0, 0]
    y_pred = [1, 1, 1, 0, 0, 0]
    assert recall_score_binary(y_true, y_pred) == 0.75


def test_false_positive_rate_simple_case():
    # I have 4 benign flows and I wrongly flag 1 of them
    y_true = [0, 0, 0, 0, 1, 1]
    y_pred = [1, 0, 0, 0, 1, 1]
    assert false_positive_rate(y_true, y_pred) == 0.25


def test_bootstrap_ci_contains_mean():
    # I expect the mean to sit inside its own confidence interval
    mean, low, high = bootstrap_ci([0.8, 0.82, 0.79, 0.81, 0.80])
    assert low <= mean <= high


def test_bootstrap_ci_is_repeatable():
    # I expect the same seed to give the same interval
    first = bootstrap_ci([0.1, 0.5, 0.9, 0.3], seed=7)
    second = bootstrap_ci([0.1, 0.5, 0.9, 0.3], seed=7)
    assert first == second
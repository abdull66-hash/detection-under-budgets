"""Shared metric helpers I will reuse in all three projects."""

import numpy as np
from sklearn.metrics import f1_score, average_precision_score


def bootstrap_ci(values, n_boot=1000, alpha=0.05, seed=0):
    """I will return the mean and a 95% bootstrap confidence interval."""
    values = np.asarray(values, dtype=float)

    # I will use my own random generator so the result is repeatable
    rng = np.random.default_rng(seed)

    # I will resample my values with replacement many times
    boot_means = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        boot_means.append(sample.mean())

    # I will take the 2.5th and 97.5th percentiles as the interval
    low = np.percentile(boot_means, 100 * alpha / 2)
    high = np.percentile(boot_means, 100 * (1 - alpha / 2))
    return float(values.mean()), float(low), float(high)


def recall_score_binary(y_true, y_pred):
    """I will compute recall: of all real attacks, how many did I catch."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # I will count real attacks and the ones I flagged
    positives = (y_true == 1).sum()
    if positives == 0:
        return float("nan")
    caught = ((y_true == 1) & (y_pred == 1)).sum()
    return float(caught / positives)


def false_positive_rate(y_true, y_pred):
    """I will compute the false positive rate: benign flows wrongly flagged."""
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)

    # I will count benign flows and the ones I wrongly flagged
    negatives = (y_true == 0).sum()
    if negatives == 0:
        return float("nan")
    false_alarms = ((y_true == 0) & (y_pred == 1)).sum()
    return float(false_alarms / negatives)


def macro_f1(y_true, y_pred):
    """I will compute macro-F1, which treats every class equally."""
    return float(f1_score(y_true, y_pred, average="macro", zero_division=0))


def pr_auc(y_true, y_score):
    """I will compute PR-AUC from predicted scores (good for rare attacks)."""
    return float(average_precision_score(y_true, y_score))
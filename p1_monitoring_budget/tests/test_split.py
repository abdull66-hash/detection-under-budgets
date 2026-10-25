"""Tests for the train, scorer and test split."""

import pandas as pd

from p1_monitoring_budget.src.preprocess import split_data

# Same settings as p1.yaml
CONFIG = {"split": {"seed": 0, "test_size": 0.3, "scorer_size": 0.1}}


def make_data():
    # A small fake table: many benign rows and a few rare attack classes
    classes = ["Benign"] * 1800 + ["A"] * 120 + ["B"] * 70 + ["C"] * 10
    return pd.DataFrame({"Attack": classes, "x": range(len(classes))})


def test_no_row_is_in_two_parts():
    df = make_data()
    train, scorer, test = split_data(df, CONFIG)

    # The three parts must not share any row
    assert set(train.index).isdisjoint(scorer.index)
    assert set(train.index).isdisjoint(test.index)
    assert set(scorer.index).isdisjoint(test.index)

    # Together they must hold every row
    assert len(train) + len(scorer) + len(test) == len(df)


def test_class_shares_are_kept():
    df = make_data()
    train, scorer, test = split_data(df, CONFIG)

    # The share of benign rows must be about the same in every part
    overall = (df["Attack"] == "Benign").mean()
    for part in (train, scorer, test):
        assert abs((part["Attack"] == "Benign").mean() - overall) < 0.02


def test_same_result_every_time():
    df = make_data()
    first = split_data(df, CONFIG)
    second = split_data(df, CONFIG)

    # The same settings must give the same rows
    for a, b in zip(first, second):
        assert list(a.index) == list(b.index)


def test_rare_class_is_in_every_part():
    df = make_data()
    parts = split_data(df, CONFIG)

    # Class C has only 10 rows, but it must appear in all three parts
    for part in parts:
        assert (part["Attack"] == "C").sum() >= 1
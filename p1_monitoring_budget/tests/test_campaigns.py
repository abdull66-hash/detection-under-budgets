"""Tests for campaigns and campaign-level detection."""

import numpy as np
import pandas as pd

from p1_monitoring_budget.src.campaigns import campaign_detection, make_campaign_ids

COLUMNS = ["Attack", "IPV4_SRC_ADDR", "IPV4_DST_ADDR"]


def make_table():
    # Campaign A has 12 flows (rows 0-11), campaign B has 12 flows (rows 12-23),
    # campaign C has only 3 flows, and there are 20 benign flows
    rows = (
        [("Exploits", "1.1.1.1", "2.2.2.2", 1)] * 12
        + [("Fuzzers", "1.1.1.1", "2.2.2.2", 1)] * 12
        + [("DoS", "3.3.3.3", "2.2.2.2", 1)] * 3
        + [("Benign", "4.4.4.4", "2.2.2.2", 0)] * 20
    )
    return pd.DataFrame(rows, columns=COLUMNS + ["Label"])


def test_small_campaign_is_dropped():
    ids, n = make_campaign_ids(make_table(), COLUMNS, 10)

    # Only A and B are big enough, the 3 DoS flows get -1
    assert n == 2
    assert (ids[24:27] == -1).all()


def test_benign_flows_have_no_campaign():
    ids, n = make_campaign_ids(make_table(), COLUMNS, 10)
    assert (ids[27:] == -1).all()


def test_nothing_detected():
    df = make_table()
    ids, n = make_campaign_ids(df, COLUMNS, 10)
    detected = np.zeros(len(df), dtype=bool)
    assert campaign_detection(ids, n, detected) == 0.0


def test_everything_detected():
    df = make_table()
    ids, n = make_campaign_ids(df, COLUMNS, 10)
    detected = np.ones(len(df), dtype=bool)
    assert campaign_detection(ids, n, detected) == 1.0


def test_one_flow_is_enough():
    df = make_table()
    ids, n = make_campaign_ids(df, COLUMNS, 10)

    # One detected flow in campaign A means 1 of 2 campaigns is detected
    detected = np.zeros(len(df), dtype=bool)
    detected[0] = True
    assert campaign_detection(ids, n, detected) == 0.5


def test_two_flows_of_one_campaign_count_once():
    df = make_table()
    ids, n = make_campaign_ids(df, COLUMNS, 10)

    # Two detected flows, both in campaign A: still 1 of 2
    detected = np.zeros(len(df), dtype=bool)
    detected[0] = True
    detected[5] = True
    assert campaign_detection(ids, n, detected) == 0.5
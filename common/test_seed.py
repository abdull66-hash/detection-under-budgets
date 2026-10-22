"""Tiny test that checks my seed function really makes results repeatable."""

import numpy as np

from common.seed import set_all_seeds


def test_same_seed_gives_same_numbers():
    # I will draw numbers twice with the same seed
    set_all_seeds(42)
    first = np.random.rand(5)
    set_all_seeds(42)
    second = np.random.rand(5)

    # I expect both draws to be identical
    assert np.array_equal(first, second)


def test_different_seed_gives_different_numbers():
    # I will draw numbers with two different seeds
    set_all_seeds(1)
    first = np.random.rand(5)
    set_all_seeds(2)
    second = np.random.rand(5)

    # I expect the draws to differ
    assert not np.array_equal(first, second)
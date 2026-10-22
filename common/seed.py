"""Helper to make my experiments reproducible by fixing every random seed."""

import os
import random

import numpy as np


def set_all_seeds(seed: int) -> None:
    """I will set the seed for every random number generator I use."""
    # Fix Python's built-in random module
    random.seed(seed)

    # I will fix numpy, which pandas and scikit-learn use internally
    np.random.seed(seed)

    # I will fix hash ordering so results do not change between runs
    os.environ["PYTHONHASHSEED"] = str(seed)
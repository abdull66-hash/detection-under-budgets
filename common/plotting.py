"""Shared plotting helpers so all my figures look consistent."""

from pathlib import Path

import matplotlib.pyplot as plt


def set_style():
    """I will set one clean style that I use for every figure."""
    plt.rcParams.update({
        "figure.figsize": (6, 4),
        "figure.dpi": 100,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "legend.frameon": False,
    })


def save_figure(fig, path_without_extension):
    """I will save my figure as both PNG and PDF."""
    base = Path(path_without_extension)

    # I will make sure the output folder exists
    base.parent.mkdir(parents=True, exist_ok=True)

    # I will save a PNG for quick viewing and a PDF for the report
    fig.savefig(base.with_suffix(".png"), dpi=200, bbox_inches="tight")
    fig.savefig(base.with_suffix(".pdf"), bbox_inches="tight")
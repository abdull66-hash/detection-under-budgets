"""Small test that checks my figure saving creates both files."""

import matplotlib

# I will use a backend that needs no window, so the test runs anywhere
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from common.plotting import set_style, save_figure


def test_save_figure_creates_png_and_pdf(tmp_path):
    # I will draw a tiny plot
    set_style()
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_xlabel("x")
    ax.set_ylabel("y")

    # I will save it into a temporary folder
    save_figure(fig, tmp_path / "demo")
    plt.close(fig)

    # I expect both files to exist
    assert (tmp_path / "demo.png").exists()
    assert (tmp_path / "demo.pdf").exists()
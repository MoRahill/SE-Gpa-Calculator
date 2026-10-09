"""Generates a PNG chart of a student's GPA trend across semesters, using
matplotlib with the non-interactive 'Agg' backend (required since this runs
server-side with no display)."""

import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_gpa_trend_chart(semester_gpas: list[dict]) -> bytes:
    """semester_gpas: list of {'term': str, 'gpa': float}, already sorted in
    the order they should appear on the x-axis. Returns PNG image bytes."""
    terms = [s["term"] for s in semester_gpas]
    gpas = [s["gpa"] for s in semester_gpas]

    fig, ax = plt.subplots(figsize=(7, 4), dpi=120)

    if terms:
        ax.plot(terms, gpas, marker="o", linewidth=2, color="#3b5bdb")
        ax.fill_between(range(len(terms)), gpas, alpha=0.08, color="#3b5bdb")
    else:
        ax.text(0.5, 0.5, "No course data yet", ha="center", va="center", transform=ax.transAxes, color="#888")

    ax.set_ylim(0, 4.0)
    ax.set_ylabel("GPA")
    ax.set_title("GPA by semester")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer.getvalue()

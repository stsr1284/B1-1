"""실제 관측값을 나타내는 제출용 PNG. 그래프에는 영어, 리포트에는 한국어 설명."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .clean import MODES

COLORS = {"bike": "#149D8D", "bus": "#DC8036", "subway": "#5475D3"}
LABELS = {"bike": "Bike rentals", "bus": "Bus boardings", "subway": "Subway boardings"}


def make_plots(features: pd.DataFrame, stats: dict, folder: Path) -> list[str]:
    folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "bold",
            "figure.facecolor": "white",
        }
    )
    names = []

    def save(fig, name):
        fig.savefig(folder / name, dpi=160, bbox_inches="tight", metadata={"Software": "B3-1"})
        plt.close(fig)
        names.append(name)

    fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True, layout="constrained")
    for ax, mode in zip(axes, MODES):
        part = features[features["mode"] == mode]
        ax.plot(
            part["date"], part["value"] / 1000, color=COLORS[mode], alpha=0.3, lw=0.8, label="Daily"
        )
        ax.plot(
            part["date"], part["rolling7"] / 1000, color=COLORS[mode], lw=1.8, label="7-day mean"
        )
        ax.set(title=LABELS[mode], ylabel="1,000 events")
        ax.grid(alpha=0.15)
        ax.legend(loc="upper right", frameon=False)
    axes[-1].set_xlabel("Date (2025); each panel has its own scale")
    fig.suptitle("Daily mobility demand | Seoul public datasets, 2025", fontsize=16)
    save(fig, "01_daily_trends.png")

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), layout="constrained")
    for ax, mode in zip(axes, MODES):
        values = stats["modes"][mode]["weekday_means"]
        ax.bar(range(7), [values[str(i)] / 1000 for i in range(7)], color=COLORS[mode], alpha=0.85)
        ax.set_xticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
        ax.tick_params(axis="x", labelrotation=35)
        ax.set(title=LABELS[mode], ylabel="Daily mean (1,000 events)")
        ax.grid(axis="y", alpha=0.15)
    fig.suptitle("Weekday patterns | 2025 (public holidays retain their calendar weekday)")
    save(fig, "02_weekday_patterns.png")

    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")
    for mode in MODES:
        s = stats["modes"][mode]
        ax.plot(
            range(1, 13),
            [s["monthly_daily_means"][str(m)] / s["average"] * 100 for m in range(1, 13)],
            marker="o",
            color=COLORS[mode],
            label=LABELS[mode],
        )
    ax.axhline(100, color="gray", ls="--", lw=1)
    ax.set(
        title="Monthly daily averages | 2025 annual daily mean = 100",
        xlabel="Month (2025)",
        ylabel="Index (not transport mode share)",
        xticks=range(1, 13),
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.15)
    save(fig, "03_monthly_patterns.png")

    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True, layout="constrained")
    for ax, mode in zip(axes, MODES):
        part = features[features["mode"] == mode]
        ax.plot(part["date"], part["deviation_pct"], color=COLORS[mode], lw=0.8)
        ax.axhline(30, color="gray", ls="--", lw=0.8)
        ax.axhline(-30, color="gray", ls="--", lw=0.8)
        extreme = part.loc[part["deviation_pct"].abs().idxmax()]
        ax.annotate(
            extreme["date"].strftime("%m-%d"),
            (extreme["date"], extreme["deviation_pct"]),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=9,
        )
        ax.set(title=LABELS[mode], ylabel="Deviation (%)")
        ax.grid(alpha=0.15)
    axes[-1].set_xlabel("Date (2025)")
    fig.suptitle(
        "Unusual days | relative to same-month, same-weekday mean\nRetrospective comparison; dashed lines: +/-30%",
        fontsize=14,
    )
    save(fig, "04_unusual_days.png")
    return names

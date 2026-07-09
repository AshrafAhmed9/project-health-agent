import matplotlib

matplotlib.use("Agg")  # Thread-safe non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List

# Setup visual styling
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)


def generate_trend_chart(
    weeks: List[str],
    s2p_scores: List[float],
    planb_scores: List[float],
    output_path: Path,
):
    """
    Line chart showing composite scores across three weeks for both projects.
    """
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)

    # Draw background RAG bands
    ax.axhspan(70, 100, alpha=0.1, color="#2ECC71", label="Green Zone (>= 70)")
    ax.axhspan(40, 70, alpha=0.1, color="#F5A623", label="Amber Zone (40-70)")
    ax.axhspan(0, 40, alpha=0.1, color="#E83E3E", label="Red Zone (< 40)")

    # Plot project trajectories
    ax.plot(
        weeks,
        s2p_scores,
        color="#1B2A4A",
        marker="o",
        linewidth=3,
        markersize=8,
        label="S2P Project (Titan)",
    )
    ax.plot(
        weeks,
        planb_scores,
        color="#0096D6",
        marker="s",
        linewidth=3,
        markersize=8,
        label="Project Plan B (UniSan)",
    )

    # Titles and formatting
    ax.set_title(
        "Project Health Score Trends (Composite 3-Week View)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylabel("Composite Score (0 - 100)", fontsize=11, fontweight="bold")
    ax.set_xlabel("Reporting Week", fontsize=11, fontweight="bold")
    ax.set_ylim(0, 105)

    # Add values on points
    for i, txt in enumerate(s2p_scores):
        ax.annotate(
            f"{txt:.0f}",
            (weeks[i], s2p_scores[i] + 2),
            fontsize=10,
            fontweight="bold",
            ha="center",
            color="#1B2A4A",
        )
    for i, txt in enumerate(planb_scores):
        ax.annotate(
            f"{txt:.0f}",
            (weeks[i], planb_scores[i] - 4),
            fontsize=10,
            fontweight="bold",
            ha="center",
            color="#0096D6",
        )

    ax.legend(loc="lower left", frameon=True, facecolor="white", edgecolor="lightgray")
    ax.grid(True, linestyle="--", alpha=0.5)

    # Save chart
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path, facecolor="white")
    plt.close(fig)
    print(f"📈 Trend chart generated at {output_path}")


def generate_resource_donut(
    s2p_assigned: int,
    s2p_unassigned: int,
    planb_assigned: int,
    planb_unassigned: int,
    output_path: Path,
):
    """
    Double donut chart or side-by-side bar chart showing unassigned active tasks.
    We'll do a side-by-side grouped bar chart since it's cleaner to compare.
    """
    fig, ax = plt.subplots(figsize=(8, 4), dpi=150)

    projects = ["S2P Project (Titan)", "Project Plan B (UniSan)"]
    assigned = [s2p_assigned, planb_assigned]
    unassigned = [s2p_unassigned, planb_unassigned]

    x = range(len(projects))
    width = 0.35

    # Color variables matching corporate colors
    rects1 = ax.bar(
        [i - width / 2 for i in x],
        assigned,
        width,
        label="Assigned Tasks",
        color="#2D4A7A",
    )
    rects2 = ax.bar(
        [i + width / 2 for i in x],
        unassigned,
        width,
        label="Unassigned Tasks",
        color="#E83E3E",
    )

    ax.set_title(
        "Resource Assignment Gaps (Active Tasks)",
        fontsize=12,
        fontweight="bold",
        pad=15,
    )
    ax.set_ylabel("Number of Active Tasks", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(projects, fontsize=10, fontweight="bold")
    ax.legend(frameon=True, facecolor="white")

    # Attach labels above bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(
                f"{height}",
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    fig.savefig(output_path, facecolor="white")
    plt.close(fig)
    print(f"📊 Resource coverage chart generated at {output_path}")

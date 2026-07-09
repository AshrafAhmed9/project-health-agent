from src.config import SIGNAL_WEIGHTS
from src.ingestion.normalizer import ProjectData
from src.analysis.schedule_analyzer import SignalResult, score_to_rag


def analyze_velocity(project_data: ProjectData) -> SignalResult:
    summary = project_data.summary
    ref_date = summary.reference_date

    total_duration = (summary.project_end - summary.project_start).days
    elapsed = (ref_date - summary.project_start).days

    if total_duration <= 0:
        elapsed_ratio = 1.0
    else:
        elapsed_ratio = min(max(elapsed / total_duration, 0.0), 1.0)

    pct_complete = summary.percent_complete

    if elapsed_ratio <= 0.01:
        velocity_ratio = 1.0
    else:
        velocity_ratio = pct_complete / elapsed_ratio

    # Score based on velocity ratio
    if velocity_ratio >= 0.95:
        score = 100
    elif velocity_ratio >= 0.80:
        score = 70
    elif velocity_ratio >= 0.60:
        score = 40
    else:
        score = 15

    detail = f"Task Completion Velocity Ratio: {velocity_ratio:.2f} ({pct_complete*100:.1f}% actual progress vs {elapsed_ratio*100:.1f}% elapsed timeline)."

    return SignalResult(
        name="Task Completion Velocity",
        score=float(score),
        weight=SIGNAL_WEIGHTS["task_velocity"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "velocity_ratio": velocity_ratio,
            "elapsed_ratio": elapsed_ratio,
            "pct_complete": pct_complete,
        },
    )

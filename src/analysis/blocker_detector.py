from src.config import SIGNAL_WEIGHTS
from src.ingestion.normalizer import ProjectData, TaskStatus
from src.analysis.schedule_analyzer import SignalResult, score_to_rag


def analyze_blockers(project_data: ProjectData) -> SignalResult:
    ref_date = project_data.summary.reference_date
    tasks = project_data.tasks

    # 1. Count explicitly On Hold tasks
    on_hold_tasks = [t for t in tasks if t.status == TaskStatus.ON_HOLD or t.on_hold]
    on_hold_count = len(on_hold_tasks)

    # 2. Count stalled tasks: In Progress with progress < 10% but planned_start was > 14 days ago
    stalled_tasks = []
    for t in tasks:
        if t.status == TaskStatus.IN_PROGRESS and t.percent_complete < 0.1:
            if t.planned_start and (ref_date - t.planned_start).days > 14:
                stalled_tasks.append(t)

    stalled_count = len(stalled_tasks)

    # 3. Count at risk tasks
    at_risk_tasks = [t for t in tasks if t.at_risk]
    at_risk_count = len(at_risk_tasks)

    total_blockers = on_hold_count + stalled_count + at_risk_count

    # Active tasks (In Progress, Not Started, On Hold)
    active_tasks = [
        t
        for t in tasks
        if t.status
        in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)
    ]
    active_count = len(active_tasks)

    if active_count == 0:
        blocker_ratio = 0.0
    else:
        blocker_ratio = total_blockers / active_count

    # Score based on blocker ratio
    if blocker_ratio == 0:
        score = 100
    elif blocker_ratio < 0.02:
        score = 85
    elif blocker_ratio < 0.05:
        score = 60
    elif blocker_ratio < 0.10:
        score = 35
    else:
        score = 10

    # Detail message
    details = []
    if on_hold_count > 0:
        details.append(f"{on_hold_count} tasks On Hold")
    if stalled_count > 0:
        details.append(f"{stalled_count} stalled tasks")
    if at_risk_count > 0:
        details.append(f"{at_risk_count} tasks flagged At Risk")

    if not details:
        detail = "No active blockers, stalled, or at-risk tasks detected."
    else:
        detail = (
            ", ".join(details) + f" (Ratio: {blocker_ratio*100:.1f}% of active tasks)."
        )

    return SignalResult(
        name="Blocker Density",
        score=float(score),
        weight=SIGNAL_WEIGHTS["blocker_density"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "on_hold_count": on_hold_count,
            "stalled_count": stalled_count,
            "at_risk_count": at_risk_count,
            "total_blockers": total_blockers,
            "active_tasks_count": active_count,
            "blocker_ratio": blocker_ratio,
        },
    )

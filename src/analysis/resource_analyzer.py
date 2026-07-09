from src.config import SIGNAL_WEIGHTS
from src.ingestion.normalizer import ProjectData, TaskStatus
from src.analysis.schedule_analyzer import SignalResult, score_to_rag


def analyze_resources(project_data: ProjectData) -> SignalResult:
    tasks = project_data.tasks

    # Analyze coverage for active tasks (not completed or NA)
    active_tasks = [
        t
        for t in tasks
        if t.status
        in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)
    ]
    total_active = len(active_tasks)

    if total_active == 0:
        coverage = 1.0
        unassigned_count = 0
    else:
        assigned_tasks = [
            t
            for t in active_tasks
            if t.assigned_to
            and str(t.assigned_to).strip()
            and str(t.assigned_to).lower() != "none"
        ]
        assigned_count = len(assigned_tasks)
        unassigned_count = total_active - assigned_count
        coverage = assigned_count / total_active

    # Score based on coverage
    if coverage >= 0.90:
        score = 100
    elif coverage >= 0.70:
        score = 70
    elif coverage >= 0.50:
        score = 40
    else:
        score = 15

    detail = f"Resource assignment coverage is {coverage*100:.1f}%. {unassigned_count} of {total_active} active tasks have no assigned owner."

    return SignalResult(
        name="Resource Coverage",
        score=float(score),
        weight=SIGNAL_WEIGHTS["resource_coverage"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "total_active_tasks": total_active,
            "unassigned_count": unassigned_count,
            "coverage_ratio": coverage,
        },
    )

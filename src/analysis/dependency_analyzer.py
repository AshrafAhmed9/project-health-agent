from src.config import SIGNAL_WEIGHTS, RAGStatus
from src.ingestion.normalizer import ProjectData, TaskStatus
from src.analysis.schedule_analyzer import SignalResult, score_to_rag

def analyze_dependencies(project_data: ProjectData) -> SignalResult:
    tasks = project_data.tasks
    active_tasks = [t for t in tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)]
    total_active = len(active_tasks)
    
    # 1. Critical tasks analysis
    critical_tasks = [t for t in tasks if t.is_critical]
    total_critical = len(critical_tasks)
    
    critical_delayed = 0
    for t in critical_tasks:
        # Check if behind schedule
        if t.status != TaskStatus.COMPLETED:
            if t.variance_days is not None and t.variance_days < -5:
                critical_delayed += 1
            elif t.schedule_health in ("Red", "Yellow"):
                critical_delayed += 1
                
    critical_delay_ratio = critical_delayed / max(total_critical, 1)
    
    # 2. Total Float/Slack analysis
    # Tasks with float <= 3 days (excluding completed)
    low_float_tasks = [t for t in active_tasks if t.total_float is not None and t.total_float <= 3]
    low_float_count = len(low_float_tasks)
    low_float_ratio = low_float_count / max(total_active, 1)
    
    # Calculate score
    if critical_delayed == 0 and low_float_ratio < 0.1:
        score = 100
    elif critical_delay_ratio < 0.1 or low_float_ratio < 0.2:
        score = 70
    elif critical_delay_ratio < 0.3 or low_float_ratio < 0.4:
        score = 40
    else:
        score = 15
        
    detail = f"Dependency risk: {critical_delayed} of {total_critical} critical path tasks are delayed. " \
             f"{low_float_count} active tasks have low schedule float (<= 3 days)."
             
    return SignalResult(
        name="Dependency Risk",
        score=float(score),
        weight=SIGNAL_WEIGHTS["dependency_risk"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "total_critical": total_critical,
            "critical_delayed": critical_delayed,
            "critical_delay_ratio": critical_delay_ratio,
            "low_float_count": low_float_count,
            "low_float_ratio": low_float_ratio
        }
    )

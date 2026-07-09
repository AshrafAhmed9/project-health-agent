from datetime import date
from src.config import SIGNAL_WEIGHTS, RAGStatus
from src.ingestion.normalizer import ProjectData, NormalizedTask, TaskStatus
from src.analysis.schedule_analyzer import SignalResult, score_to_rag

def analyze_milestones(project_data: ProjectData) -> SignalResult:
    ref_date = project_data.summary.reference_date
    milestones = project_data.milestones
    
    scored_milestones = []
    milestone_details = []
    
    # Filter out Level 0 (the project wrapper task itself) to avoid double counting
    l1_milestones = [m for m in milestones if m.level == 1]
    
    if not l1_milestones:
        # Fallback to level 0 or any milestones if level 1 is empty
        l1_milestones = milestones
        
    for m in l1_milestones:
        # Check if it should be complete
        if m.planned_end and m.planned_end < ref_date:
            # Should be completed
            if m.status == TaskStatus.COMPLETED:
                m_score = 100
                m_detail = f"{m.task_name}: Completed on time"
            elif m.status == TaskStatus.IN_PROGRESS:
                if m.percent_complete >= 0.90:
                    m_score = 70
                    m_detail = f"{m.task_name}: Missed deadline but near completion ({m.percent_complete*100:.0f}%)"
                else:
                    m_score = 30
                    m_detail = f"{m.task_name}: Past due and significantly behind ({m.percent_complete*100:.0f}%)"
            else: # Not Started or On Hold
                m_score = 0
                m_detail = f"{m.task_name}: Past due and not started"
            scored_milestones.append(m_score)
            milestone_details.append(m_detail)
            
        elif m.planned_start and m.planned_end and m.planned_start <= ref_date <= m.planned_end:
            # Active Milestone
            duration = (m.planned_end - m.planned_start).days
            elapsed = (ref_date - m.planned_start).days
            expected_progress = elapsed / max(duration, 1)
            actual_progress = m.percent_complete
            
            if actual_progress >= expected_progress * 0.9:
                m_score = 90
                m_detail = f"{m.task_name}: Active and on track ({actual_progress*100:.0f}% vs expected {expected_progress*100:.0f}%)"
            elif actual_progress >= expected_progress * 0.7:
                m_score = 60
                m_detail = f"{m.task_name}: Active with slight delay ({actual_progress*100:.0f}% vs expected {expected_progress*100:.0f}%)"
            else:
                m_score = 25
                m_detail = f"{m.task_name}: Active and severely behind ({actual_progress*100:.0f}% vs expected {expected_progress*100:.0f}%)"
            scored_milestones.append(m_score)
            milestone_details.append(m_detail)
            
        # Future milestones are not scored to avoid skewing the average
        
    if not scored_milestones:
        # If no active/past milestones, score as 100 (good health)
        score = 100.0
        detail = "No active or past due milestones to evaluate."
    else:
        score = sum(scored_milestones) / len(scored_milestones)
        # Summarize top 3 milestones in detail string
        detail = "; ".join(milestone_details[:4])
        if len(milestone_details) > 4:
            detail += f" (+{len(milestone_details)-4} more)"
            
    return SignalResult(
        name="Milestone Health",
        score=float(score),
        weight=SIGNAL_WEIGHTS["milestone_health"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "milestone_count": len(l1_milestones),
            "scored_count": len(scored_milestones),
            "raw_scores": scored_milestones
        }
    )

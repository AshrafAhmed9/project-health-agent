from datetime import date
from src.config import SIGNAL_WEIGHTS, RAGStatus
from src.ingestion.normalizer import ProjectData
from typing import Dict, Any

class SignalResult:
    def __init__(self, name: str, score: float, weight: float, rag: RAGStatus, detail: str, metrics: Dict[str, Any]):
        self.signal_name = name
        self.score = score
        self.weight = weight
        self.weighted_score = score * weight
        self.rag = rag
        self.detail = detail
        self.raw_metrics = metrics

def score_to_rag(score: float) -> RAGStatus:
    if score >= 70:
        return RAGStatus.GREEN
    elif score >= 40:
        return RAGStatus.AMBER
    else:
        return RAGStatus.RED

def analyze_schedule(project_data: ProjectData) -> SignalResult:
    summary = project_data.summary
    ref_date = summary.reference_date
    
    total_duration = (summary.project_end - summary.project_start).days
    elapsed = (ref_date - summary.project_start).days
    
    if total_duration <= 0:
        elapsed_ratio = 1.0
    else:
        elapsed_ratio = min(max(elapsed / total_duration, 0.0), 1.0)
        
    pct = summary.percent_complete
    
    # Calculate SPI
    if elapsed_ratio <= 0.01:
        spi = 1.0
    else:
        spi = pct / elapsed_ratio
        
    # Score based on SPI
    if spi >= 0.95:
        score = 100
    elif spi >= 0.85:
        score = 70
    elif spi >= 0.70:
        score = 40
    else:
        score = 20
        
    # Variance Penalty
    max_negative_variance = 0
    for task in project_data.milestones:
        if task.variance_days is not None and task.variance_days < max_negative_variance:
            max_negative_variance = task.variance_days
            
    # Apply capping based on variance
    if max_negative_variance < -20:
        score = min(score, 30)
        detail_var = f"Critical schedule slippage of {abs(max_negative_variance)} days detected."
    elif max_negative_variance < -10:
        score = min(score, 50)
        detail_var = f"Moderate schedule slippage of {abs(max_negative_variance)} days detected."
    else:
        detail_var = f"Max schedule slippage is {abs(max_negative_variance)} days."
        
    detail = f"SPI = {spi:.2f}. Project is {pct*100:.1f}% complete vs {elapsed_ratio*100:.1f}% elapsed timeline. {detail_var}"
    
    return SignalResult(
        name="Schedule Performance",
        score=float(score),
        weight=SIGNAL_WEIGHTS["schedule_performance"],
        rag=score_to_rag(score),
        detail=detail,
        metrics={
            "spi": spi,
            "elapsed_ratio": elapsed_ratio,
            "worst_variance": max_negative_variance,
            "pct_complete": pct
        }
    )

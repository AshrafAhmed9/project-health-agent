from typing import List, Dict, Any, Optional
from src.analysis.rag_engine import RAGResult

class TrendAnalysis:
    def __init__(self, direction: str, delta: float, signal_trends: Dict[str, str], emerging_risks: List[str], insights: List[str]):
        self.overall_direction = direction  # "IMPROVING", "STABLE", "DECLINING"
        self.score_delta = delta
        self.signal_trends = signal_trends  # Map signal name to "↑" (improving), "↓" (declining), "→" (stable)
        self.emerging_risks = emerging_risks
        self.insights = insights

def analyze_weekly_trends(current: RAGResult, historical: List[RAGResult]) -> TrendAnalysis:
    """
    Compares the current RAGResult against a list of historical weekly RAGResults.
    historical[0] should be the most recent historical week (e.g., 1 week ago).
    """
    if not historical:
        # No history available
        return TrendAnalysis(
            direction="STABLE",
            delta=0.0,
            signal_trends={s.signal_name: "→" for s in current.signals},
            emerging_risks=[],
            insights=["Initial reporting period. No historical trend data available."]
        )
        
    last_week = historical[0]
    score_delta = current.composite_score - last_week.composite_score
    
    # Determine direction
    if score_delta > 3.0:
        direction = "IMPROVING"
    elif score_delta < -3.0:
        direction = "DECLINING"
    else:
        direction = "STABLE"
        
    # Per-signal trends
    signal_trends = {}
    current_map = {s.signal_name: s.score for s in current.signals}
    last_map = {s.signal_name: s.score for s in last_week.signals}
    
    for name, curr_score in current_map.items():
        prev_score = last_map.get(name)
        if prev_score is None:
            signal_trends[name] = "→"
        elif curr_score > prev_score + 1.0:
            signal_trends[name] = "↑"
        elif curr_score < prev_score - 1.0:
            signal_trends[name] = "↓"
        else:
            signal_trends[name] = "→"
            
    # Identify emerging risks
    emerging_risks = []
    insights = []
    
    # Look for signals that went from healthy to failing
    for s in current.signals:
        prev_sig = next((ps for ps in last_week.signals if ps.signal_name == s.signal_name), None)
        if prev_sig:
            if prev_sig.score >= 70 and s.score < 40:
                emerging_risks.append(f"Critical decline in {s.signal_name} (fell from {prev_sig.score:.0f} to {s.score:.0f})")
            elif prev_sig.score >= 70 and s.score < 70:
                emerging_risks.append(f"Decline in {s.signal_name} (fell from {prev_sig.score:.0f} to {s.score:.0f})")
                
    # Add general observations
    insights.append(f"Composite health score changed by {score_delta:+.1f} points since last week.")
    if direction == "DECLINING":
        insights.append("Project trajectory is declining. Urgent corrective actions needed.")
    elif direction == "IMPROVING":
        insights.append("Project trajectory is improving. Corrective actions are yielding results.")
        
    return TrendAnalysis(
        direction=direction,
        delta=score_delta,
        signal_trends=signal_trends,
        emerging_risks=emerging_risks,
        insights=insights
    )

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from src.config import (
    RAGStatus,
    RAG_GREEN_THRESHOLD,
    RAG_AMBER_THRESHOLD,
    RED_OVERRIDE_SINGLE_HEAVY,
    RED_OVERRIDE_SINGLE_MEDIUM,
    RED_OVERRIDE_MULTI_COUNT,
    AMBER_OVERRIDE_MULTI_COUNT,
    LOW_CONFIDENCE_THRESHOLD,
    INSUFFICIENT_DATA_THRESHOLD,
)
from src.ingestion.normalizer import ProjectData
from src.analysis.schedule_analyzer import analyze_schedule, SignalResult
from src.analysis.milestone_tracker import analyze_milestones
from src.analysis.velocity_analyzer import analyze_velocity
from src.analysis.blocker_detector import analyze_blockers
from src.analysis.resource_analyzer import analyze_resources
from src.analysis.dependency_analyzer import analyze_dependencies


@dataclass
class RAGResult:
    overall_rag: RAGStatus
    composite_score: float  # 0-100
    signals: List[SignalResult]  # All 6 signals
    override_applied: Optional[str] = None
    data_confidence: float = 1.0  # 0.0-1.0
    confidence_warning: Optional[str] = None
    reasoning_context: Optional[Dict[str, Any]] = None


class RAGEngine:
    """
    Computes overall RAG status and aggregates all signals.
    """

    def compute_rag(self, project_data: ProjectData) -> RAGResult:
        # 1. Run all 6 analyzers
        signals = [
            analyze_schedule(project_data),
            analyze_milestones(project_data),
            analyze_velocity(project_data),
            analyze_blockers(project_data),
            analyze_resources(project_data),
            analyze_dependencies(project_data),
        ]

        # 2. Calculate composite score
        composite_score = sum(s.weighted_score for s in signals)

        # Determine RAG from composite
        if composite_score >= RAG_GREEN_THRESHOLD:
            overall_rag = RAGStatus.GREEN
        elif composite_score >= RAG_AMBER_THRESHOLD:
            overall_rag = RAGStatus.AMBER
        else:
            overall_rag = RAGStatus.RED

        # 3. Evaluate override rules
        override_applied = None

        # Check heavy weights (Schedule Performance & Milestone Health) -> weight >= 20%
        heavy_signals_low = [
            s
            for s in signals
            if s.weight >= 0.20 and s.score <= RED_OVERRIDE_SINGLE_HEAVY
        ]
        # Check medium weights (Velocity, Blocker, Dependency) -> weight >= 15%
        medium_signals_low = [
            s
            for s in signals
            if s.weight >= 0.15 and s.score <= RED_OVERRIDE_SINGLE_MEDIUM
        ]
        # Count all signals below 40
        low_signals = [s for s in signals if s.score < 40]

        if heavy_signals_low:
            overall_rag = RAGStatus.RED
            override_applied = f"RED OVERRIDE: Critical heavy signal fail ({heavy_signals_low[0].signal_name} score <= {RED_OVERRIDE_SINGLE_HEAVY})"
        elif medium_signals_low:
            overall_rag = RAGStatus.RED
            override_applied = f"RED OVERRIDE: Critical medium signal fail ({medium_signals_low[0].signal_name} score <= {RED_OVERRIDE_SINGLE_MEDIUM})"
        elif len(low_signals) >= RED_OVERRIDE_MULTI_COUNT:
            overall_rag = RAGStatus.RED
            override_applied = f"RED OVERRIDE: Multiple signal failures ({len(low_signals)} signals scored < 40)"
        elif len(low_signals) >= AMBER_OVERRIDE_MULTI_COUNT:
            if overall_rag == RAGStatus.GREEN:
                overall_rag = RAGStatus.AMBER
                override_applied = f"AMBER OVERRIDE: Multiple signal warnings ({len(low_signals)} signals scored < 40)"

        # 4. Check data confidence
        data_confidence = project_data.data_quality_score
        confidence_warning = None

        if data_confidence < INSUFFICIENT_DATA_THRESHOLD:
            overall_rag = RAGStatus.INSUFFICIENT_DATA
            confidence_warning = (
                "INSUFFICIENT DATA: Data quality is too low for reliable analysis."
            )
        elif data_confidence < LOW_CONFIDENCE_THRESHOLD:
            confidence_warning = (
                "LOW CONFIDENCE: High volume of missing or unparseable fields."
            )

        # 5. Build reasoning context for the LLM
        reasoning_context = {
            "project_name": project_data.summary.project_name,
            "project_manager": project_data.summary.project_manager,
            "reference_date": str(project_data.summary.reference_date),
            "pct_complete": project_data.summary.percent_complete,
            "total_tasks": project_data.summary.total_tasks,
            "completed": project_data.summary.completed_count,
            "in_progress": project_data.summary.in_progress_count,
            "not_started": project_data.summary.not_started_count,
            "on_hold": project_data.summary.on_hold_count,
            "override_applied": override_applied,
            "confidence_warning": confidence_warning,
            "source_file": project_data.source_file,
            "schema_type": project_data.schema_type,
        }

        return RAGResult(
            overall_rag=overall_rag,
            composite_score=float(composite_score),
            signals=signals,
            override_applied=override_applied,
            data_confidence=data_confidence,
            confidence_warning=confidence_warning,
            reasoning_context=reasoning_context,
        )

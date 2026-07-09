import pytest
from datetime import date
from src.config import RAGStatus, TaskStatus
from src.ingestion.normalizer import ProjectData, ProjectSummary, NormalizedTask
from src.analysis.rag_engine import RAGEngine

def test_rag_engine_green_project():
    summary = ProjectSummary(
        project_name="Green Test Project",
        project_manager="Test PM",
        project_start=date(2026, 1, 1),
        project_end=date(2026, 12, 31),
        percent_complete=0.99,
        schedule_health="Green",
        at_risk="Low",
        duration_days=365,
        reference_date=date(2026, 6, 1),
        total_tasks=10,
        completed_count=9,
        in_progress_count=1,
        not_started_count=0,
        on_hold_count=0
    )
    
    # Active task
    task = NormalizedTask(
        task_name="Task 1",
        status=TaskStatus.IN_PROGRESS,
        level=2,
        phase="Build",
        planned_start=date(2026, 5, 1),
        planned_end=date(2026, 6, 15),
        actual_start=date(2026, 5, 1),
        actual_end=None,
        baseline_start=date(2026, 5, 1),
        baseline_end=date(2026, 6, 15),
        percent_complete=0.90,
        duration_days=45,
        predecessors=None,
        assigned_to="Developer 1",
        schedule_health="Green",
        variance_days=0,
        is_milestone=False,
        is_critical=False,
        on_hold=False,
        at_risk=False,
        total_float=10.0,
        status_comment=None,
        data_completeness=1.0
    )
    
    # Milestone L1
    milestone = NormalizedTask(
        task_name="Milestone 1",
        status=TaskStatus.COMPLETED,
        level=1,
        phase="Phase 1",
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 2, 28),
        actual_start=date(2026, 1, 1),
        actual_end=date(2026, 2, 28),
        baseline_start=date(2026, 1, 1),
        baseline_end=date(2026, 2, 28),
        percent_complete=1.0,
        duration_days=58,
        predecessors=None,
        assigned_to="Developer 1",
        schedule_health="Green",
        variance_days=0,
        is_milestone=True,
        is_critical=True,
        on_hold=False,
        at_risk=False,
        total_float=0.0,
        status_comment=None,
        data_completeness=1.0
    )
    
    project_data = ProjectData(
        summary=summary,
        tasks=[task, milestone],
        milestones=[milestone],
        comments=[],
        source_file="test.xlsx",
        schema_type="s2p",
        data_quality_score=1.0
    )
    
    engine = RAGEngine()
    result = engine.compute_rag(project_data)
    
    assert result.overall_rag == RAGStatus.GREEN
    assert result.composite_score >= 70.0
    assert result.override_applied is None
    assert result.data_confidence == 1.0

def test_rag_engine_red_override():
    summary = ProjectSummary(
        project_name="Red Override Project",
        project_manager="Test PM",
        project_start=date(2026, 1, 1),
        project_end=date(2026, 12, 31),
        percent_complete=0.10,
        schedule_health="Red",
        at_risk="High",
        duration_days=365,
        reference_date=date(2026, 6, 1),
        total_tasks=10,
        completed_count=1,
        in_progress_count=9,
        not_started_count=0,
        on_hold_count=0
    )
    
    # Delayed Milestone L1 -> triggers schedule slip and milestone health failure
    milestone = NormalizedTask(
        task_name="Milestone 1",
        status=TaskStatus.IN_PROGRESS,
        level=1,
        phase="Phase 1",
        planned_start=date(2026, 1, 1),
        planned_end=date(2026, 3, 31),  # Should be complete long ago (ref_date is June 1)
        actual_start=date(2026, 1, 1),
        actual_end=None,
        baseline_start=date(2026, 1, 1),
        baseline_end=date(2026, 3, 31),
        percent_complete=0.15,
        duration_days=90,
        predecessors=None,
        assigned_to="Developer 1",
        schedule_health="Red",
        variance_days=-60,  # 60 days late
        is_milestone=True,
        is_critical=True,
        on_hold=False,
        at_risk=True,
        total_float=0.0,
        status_comment=None,
        data_completeness=1.0
    )
    
    project_data = ProjectData(
        summary=summary,
        tasks=[milestone],
        milestones=[milestone],
        comments=[],
        source_file="test.xlsx",
        schema_type="s2p",
        data_quality_score=1.0
    )
    
    engine = RAGEngine()
    result = engine.compute_rag(project_data)
    
    assert result.overall_rag == RAGStatus.RED
    assert result.override_applied is not None

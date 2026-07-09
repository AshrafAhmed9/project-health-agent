"""
Integration tests that run the full analysis pipeline on real project data.
These verify that parsing → normalization → RAG scoring → report generation
works end-to-end without errors and produces meaningful outputs.
"""
import pytest
from pathlib import Path
from datetime import date
from src.config import RAGStatus, TaskStatus
from src.ingestion.parser import ExcelParser
from src.ingestion.normalizer import DataNormalizer
from src.analysis.rag_engine import RAGEngine

DATA_DIR = Path(__file__).parent.parent / "data"
REF_DATE = date(2026, 7, 2)

class TestS2PIntegration:
    """Full pipeline tests for S2P Project (Titan)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        parser = ExcelParser()
        normalizer = DataNormalizer()
        engine = RAGEngine()
        
        raw = parser.parse(DATA_DIR / "S2P Project.xlsx")
        self.project_data = normalizer.normalize(raw, REF_DATE)
        self.rag_result = engine.compute_rag(self.project_data)
    
    def test_project_name_resolved(self):
        """Project name should be extracted from L0 task since summary field is empty."""
        assert "Titan" in self.project_data.summary.project_name or "S2P" in self.project_data.summary.project_name
    
    def test_project_manager(self):
        assert self.project_data.summary.project_manager == "Aftab Hashambhai"
    
    def test_completion_percentage(self):
        assert 0.60 <= self.project_data.summary.percent_complete <= 0.80  # Should be ~71%
    
    def test_task_counts_reasonable(self):
        s = self.project_data.summary
        assert s.total_tasks > 400
        assert s.completed_count > 200
        assert s.in_progress_count > 10
        assert s.not_started_count > 100
    
    def test_milestones_extracted(self):
        assert len(self.project_data.milestones) > 10
    
    def test_on_hold_tasks_detected(self):
        """S2P has 3 On Hold tasks."""
        assert self.project_data.summary.on_hold_count == 3
    
    def test_rag_not_green(self):
        """S2P has critical issues — should NOT be GREEN."""
        assert self.rag_result.overall_rag != RAGStatus.GREEN
    
    def test_composite_score_reasonable(self):
        assert 20 <= self.rag_result.composite_score <= 80
    
    def test_all_six_signals_present(self):
        assert len(self.rag_result.signals) == 6
        signal_names = {s.signal_name for s in self.rag_result.signals}
        assert "Schedule Performance" in signal_names
        assert "Milestone Health" in signal_names
        assert "Task Completion Velocity" in signal_names
        assert "Blocker Density" in signal_names
        assert "Resource Coverage" in signal_names
        assert "Dependency Risk" in signal_names
    
    def test_resource_coverage_low(self):
        """S2P has 67.5% tasks unassigned — resource signal should be RED."""
        resource_signal = next(s for s in self.rag_result.signals if s.signal_name == "Resource Coverage")
        assert resource_signal.score <= 40  # Should be very low
    
    def test_data_confidence_high(self):
        """Data quality should be reasonable (>80%) since the files are mostly populated."""
        assert self.rag_result.data_confidence > 0.80
    
    def test_schedule_variance_detected(self):
        """The schedule signal should detect the -81d Phase 2 variance."""
        sched_signal = next(s for s in self.rag_result.signals if s.signal_name == "Schedule Performance")
        assert sched_signal.raw_metrics["worst_variance"] <= -30


class TestPlanBIntegration:
    """Full pipeline tests for Project Plan B (UniSan)."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        parser = ExcelParser()
        normalizer = DataNormalizer()
        engine = RAGEngine()
        
        raw = parser.parse(DATA_DIR / "Project Plan B.xlsx")
        self.project_data = normalizer.normalize(raw, REF_DATE)
        self.rag_result = engine.compute_rag(self.project_data)
    
    def test_project_name_resolved(self):
        assert "UniSan" in self.project_data.summary.project_name or "S2P" in self.project_data.summary.project_name
    
    def test_project_manager(self):
        assert self.project_data.summary.project_manager == "Rajat Bothra"
    
    def test_completion_percentage(self):
        assert 0.35 <= self.project_data.summary.percent_complete <= 0.55  # Should be ~44%
    
    def test_task_counts_reasonable(self):
        s = self.project_data.summary
        assert s.total_tasks > 300
        assert s.completed_count > 100
        assert s.in_progress_count > 30
        assert s.not_started_count > 150
    
    def test_no_on_hold_tasks(self):
        """Plan B has 0 On Hold tasks."""
        assert self.project_data.summary.on_hold_count == 0
    
    def test_rag_not_green(self):
        """Plan B is 44% with schedule RED — should NOT be GREEN."""
        assert self.rag_result.overall_rag != RAGStatus.GREEN
    
    def test_composite_score_reasonable(self):
        assert 20 <= self.rag_result.composite_score <= 80
    
    def test_milestones_include_training_phase(self):
        """Training Phase I should appear in milestones and have variance data."""
        training = [m for m in self.project_data.milestones if "Training Phase I" in m.task_name]
        assert len(training) > 0
        # Training Phase I has a 17-day slip
        t = training[0]
        assert t.variance_days is not None
        assert t.variance_days > 10  # 17 days behind
    
    def test_schema_detected_as_plan_b(self):
        assert self.project_data.schema_type == "plan_b"
    
    def test_phases_inferred(self):
        """Plan B has empty Phase/Milestone column — phases should be inferred from L1 task names."""
        tasks_with_phase = [t for t in self.project_data.tasks if t.phase is not None]
        assert len(tasks_with_phase) > 200  # Most tasks should have inferred phase

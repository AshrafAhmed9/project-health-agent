from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from src.config import RAGStatus, TaskStatus, settings
from dataclasses import dataclass

@dataclass
class NormalizedTask:
    task_name: str
    status: TaskStatus
    level: int                          # 0=project, 1=phase, 2+=subtask
    phase: str | None                   # Phase name (from phase_milestone col or inferred from L1 parent)
    planned_start: date | None
    planned_end: date | None
    actual_start: date | None
    actual_end: date | None
    baseline_start: date | None
    baseline_end: date | None
    percent_complete: float             # 0.0 to 1.0
    duration_days: int | None
    predecessors: str | None
    assigned_to: str | None
    schedule_health: str | None         # Original from file
    variance_days: int | None           # Negative = behind schedule
    is_milestone: bool                  # True if level <= 1
    is_critical: bool
    on_hold: bool
    at_risk: bool
    total_float: float | None
    status_comment: str | None
    data_completeness: float            # 0.0-1.0 how many fields are non-null

@dataclass
class ProjectSummary:
    project_name: str                   # From L0 task_name if summary is empty
    project_manager: str
    project_start: date
    project_end: date
    percent_complete: float
    schedule_health: str
    at_risk: str
    duration_days: int
    reference_date: date                # "Today's date" from the data
    total_tasks: int
    completed_count: int
    in_progress_count: int
    not_started_count: int
    on_hold_count: int

@dataclass  
class ProjectData:
    summary: ProjectSummary
    tasks: list[NormalizedTask]
    milestones: list[NormalizedTask]     # Only L0-L1 tasks
    comments: list[Dict[str, Any]]      # From Comments sheet
    source_file: str
    schema_type: str                    # "s2p" or "plan_b"
    data_quality_score: float           # Overall 0.0-1.0

class DataNormalizer:
    """
    Normalizes parsed task data and summary maps into structured ProjectData.
    """
    
    def _coerce_date(self, val: Any) -> date | None:
        if val is None:
            return None
        if isinstance(val, date) and not isinstance(val, datetime):
            return val
        if isinstance(val, datetime):
            return val.date()
        if isinstance(val, str):
            val = val.strip()
            if not val or val.lower() == "none" or val.startswith("#"):
                return None
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%y", "%d-%b-%Y", "%d-%m-%Y"):
                try:
                    return datetime.strptime(val, fmt).date()
                except ValueError:
                    continue
        return None

    def _coerce_float(self, val: Any) -> float | None:
        if val is None:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    def _coerce_int(self, val: Any) -> int | None:
        if val is None:
            return None
        try:
            # Handle duration fields like '170d'
            if isinstance(val, str):
                val = val.strip().replace("d", "").replace("h", "")
            return int(float(val))
        except (ValueError, TypeError):
            return None

    def _clean_variance(self, val: Any) -> int | None:
        if val is None:
            return None
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            val = val.strip().lower().replace("d", "").replace(" ", "")
            if not val or val == "none" or val.startswith("#"):
                return None
            try:
                # In S2P, variance values are like '-32d'.
                # In Plan B, we might see '17d' or '-8d'
                return int(float(val))
            except ValueError:
                return None
        return None

    def _map_status(self, status_str: Any, pct: float | None, on_hold: bool) -> TaskStatus:
        if on_hold:
            return TaskStatus.ON_HOLD
        if not status_str:
            if pct is not None:
                if pct >= 1.0:
                    return TaskStatus.COMPLETED
                elif pct > 0:
                    return TaskStatus.IN_PROGRESS
            return TaskStatus.NOT_STARTED
            
        status_clean = str(status_str).strip().lower()
        if "completed" in status_clean or status_clean == "complete" or status_clean == "1":
            return TaskStatus.COMPLETED
        elif "progress" in status_clean:
            return TaskStatus.IN_PROGRESS
        elif "hold" in status_clean:
            return TaskStatus.ON_HOLD
        elif "applicable" in status_clean or status_clean == "n/a" or status_clean == "na":
            return TaskStatus.NOT_APPLICABLE
        elif "not started" in status_clean or status_clean == "notstarted" or status_clean == "0":
            return TaskStatus.NOT_STARTED
        
        # Fallback based on completion percentage
        if pct is not None:
            if pct >= 1.0:
                return TaskStatus.COMPLETED
            elif pct > 0:
                return TaskStatus.IN_PROGRESS
        return TaskStatus.NOT_STARTED

    def normalize(self, parsed: Dict[str, Any], ref_date: date) -> ProjectData:
        schema = parsed["schema_type"]
        tasks_raw = parsed["tasks_raw"]
        summary_raw = parsed["summary"]
        comments = parsed["comments"]
        
        normalized_tasks = []
        
        # We need to map depending on schema
        for r in tasks_raw:
            if schema == "s2p":
                name = r.get("Task Name")
                status_raw = r.get("Status")
                level = self._coerce_int(r.get("Level"))
                phase = r.get("Phase/Milestone")
                p_start = self._coerce_date(r.get("Start Date"))
                p_end = self._coerce_date(r.get("End Date"))
                a_start = self._coerce_date(r.get("Start"))
                a_end = self._coerce_date(r.get("Finish"))
                b_start = self._coerce_date(r.get("Baseline Start"))
                b_end = self._coerce_date(r.get("Baseline Finish"))
                pct = self._coerce_float(r.get("% Complete"))
                duration = self._coerce_int(r.get("Duration"))
                predecessors = str(r.get("Predecessors")) if r.get("Predecessors") is not None else None
                assigned_to = r.get("Assigned To")
                health = r.get("Schedule Health")
                var_raw = r.get("Variance")
                var_days = self._clean_variance(var_raw)
                critical = str(r.get("Critical ?")).strip().lower() in ("true", "1", "yes")
                on_hold = str(r.get("On Hold?")).strip().lower() in ("true", "1", "yes") or r.get("Status") == "On Hold"
                at_risk = str(r.get("At Risk?")).strip().lower() in ("true", "1", "yes")
                total_float = self._coerce_float(r.get("Total Float"))
                status_comment = r.get("Status Comment") or r.get("Comments")
            else: # plan_b
                name = r.get("Task Name")
                status_raw = r.get("Status")
                level = self._coerce_int(r.get("Ancestors"))  # Ancestors column maps to Level
                phase = r.get("Phase/Milestone") # usually empty, will infer
                p_start = self._coerce_date(r.get("Start Date"))
                p_end = self._coerce_date(r.get("End Date"))
                a_start = self._coerce_date(r.get("Start"))
                a_end = self._coerce_date(r.get("Finish"))
                
                # Check for baseline columns. In Plan B, cols 24-25 are baseline_start/finish but empty.
                # Col 34-35 (Baseline Start2 / Baseline Finish2) have data.
                b_start = self._coerce_date(r.get("Baseline Start2")) or self._coerce_date(r.get("Baseline Start Date")) or self._coerce_date(r.get("Baseline Start"))
                b_end = self._coerce_date(r.get("Baseline Finish2")) or self._coerce_date(r.get("Baseline End Date")) or self._coerce_date(r.get("Baseline Finish"))
                
                pct = self._coerce_float(r.get("% Complete"))
                duration = self._coerce_int(r.get("Duration"))
                predecessors = str(r.get("Predecessors")) if r.get("Predecessors") is not None else None
                assigned_to = r.get("Assigned To")
                health = r.get("Schedule Health")
                
                # Variance: look at Variance2 (col 36) first, else Variance (col 26)
                var_raw = r.get("Variance2") or r.get("Variance")
                var_days = self._clean_variance(var_raw)
                
                critical = str(r.get("Critical ?")).strip().lower() in ("true", "1", "yes")
                on_hold = str(r.get("On Hold?")).strip().lower() in ("true", "1", "yes")
                at_risk = str(r.get("At Risk?")).strip().lower() in ("true", "1", "yes")
                total_float = self._coerce_float(r.get("Total Float"))
                status_comment = r.get("Status Comment") or r.get("Comments")
                
            if not name:
                continue # Skip row if it lacks task name
                
            # Clean / Impute values
            status = self._map_status(status_raw, pct, on_hold)
            
            # Impute % Complete
            if pct is None:
                if status == TaskStatus.COMPLETED:
                    pct = 1.0
                elif status == TaskStatus.NOT_STARTED:
                    pct = 0.0
                elif status == TaskStatus.ON_HOLD:
                    pct = 0.0
                elif status == TaskStatus.IN_PROGRESS:
                    pct = 0.5
                    
            # Let's count completeness
            expected_fields = [name, status_raw, level, p_start, p_end, pct, duration, assigned_to]
            data_completeness = sum(1 for f in expected_fields if f is not None) / len(expected_fields)
            
            is_milestone = level is not None and level <= 1
            
            task = NormalizedTask(
                task_name=str(name).strip(),
                status=status,
                level=level if level is not None else 2,
                phase=phase,
                planned_start=p_start,
                planned_end=p_end,
                actual_start=a_start,
                actual_end=a_end,
                baseline_start=b_start,
                baseline_end=b_end,
                percent_complete=pct,
                duration_days=duration,
                predecessors=predecessors,
                assigned_to=assigned_to if assigned_to else None,
                schedule_health=health,
                variance_days=var_days,
                is_milestone=is_milestone,
                is_critical=critical,
                on_hold=on_hold,
                at_risk=at_risk,
                total_float=total_float,
                status_comment=status_comment,
                data_completeness=data_completeness
            )
            normalized_tasks.append(task)

        # Skip tasks that are marked Not Applicable
        normalized_tasks = [t for t in normalized_tasks if t.status != TaskStatus.NOT_APPLICABLE]
        
        # If Plan B, infer phase from L1 tasks
        if schema == "plan_b":
            # Let's build a map from task indices to their phase
            # Walk through the hierarchy.
            current_phase = None
            for t in normalized_tasks:
                if t.level == 1:
                    current_phase = t.task_name
                t.phase = current_phase

        # Extract milestones (L0 and L1)
        milestones = [t for t in normalized_tasks if t.is_milestone]
        
        # Compile summary details
        completed = sum(1 for t in normalized_tasks if t.status == TaskStatus.COMPLETED)
        in_progress = sum(1 for t in normalized_tasks if t.status == TaskStatus.IN_PROGRESS)
        not_started = sum(1 for t in normalized_tasks if t.status == TaskStatus.NOT_STARTED)
        on_hold = sum(1 for t in normalized_tasks if t.status == TaskStatus.ON_HOLD)
        
        # Get project name
        proj_name = summary_raw.get("Project Name")
        if not proj_name or proj_name.startswith("#"):
            # Find the L0 task
            l0_tasks = [t for t in normalized_tasks if t.level == 0]
            if l0_tasks:
                proj_name = l0_tasks[0].task_name
            else:
                proj_name = parsed["source_file"].replace(".xlsx", "")
                
        proj_mgr = summary_raw.get("Project Manager") or "Unknown Manager"
        proj_start = self._coerce_date(summary_raw.get("Project Start Date"))
        proj_end = self._coerce_date(summary_raw.get("Project End Date"))
        
        # If dates missing from summary, infer from tasks
        if not proj_start:
            dates = [t.planned_start for t in normalized_tasks if t.planned_start]
            proj_start = min(dates) if dates else ref_date
        if not proj_end:
            dates = [t.planned_end for t in normalized_tasks if t.planned_end]
            proj_end = max(dates) if dates else ref_date
            
        overall_pct = self._coerce_float(summary_raw.get("% Complete"))
        if overall_pct is None:
            # Calculate weighted percent complete by task duration
            total_dur = sum(t.duration_days for t in normalized_tasks if t.duration_days and t.level == 1)
            if total_dur:
                completed_dur = sum(t.percent_complete * t.duration_days for t in normalized_tasks if t.duration_days and t.level == 1)
                overall_pct = completed_dur / total_dur
            else:
                overall_pct = completed / max(len(normalized_tasks), 1)
                
        sched_health = summary_raw.get("Schedule Health") or "Green"
        at_risk = summary_raw.get("At Risk") or "Low"
        duration_days = self._coerce_int(summary_raw.get("Duration")) or (proj_end - proj_start).days
        
        summary = ProjectSummary(
            project_name=proj_name,
            project_manager=proj_mgr,
            project_start=proj_start,
            project_end=proj_end,
            percent_complete=overall_pct,
            schedule_health=sched_health,
            at_risk=at_risk,
            duration_days=duration_days,
            reference_date=ref_date,
            total_tasks=len(normalized_tasks),
            completed_count=completed,
            in_progress_count=in_progress,
            not_started_count=not_started,
            on_hold_count=on_hold
        )
        
        # Overall quality is average data completeness of all tasks
        q_score = sum(t.data_completeness for t in normalized_tasks) / max(len(normalized_tasks), 1)
        
        return ProjectData(
            summary=summary,
            tasks=normalized_tasks,
            milestones=milestones,
            comments=comments,
            source_file=parsed["source_file"],
            schema_type=schema,
            data_quality_score=q_score
        )

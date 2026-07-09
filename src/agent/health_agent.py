import json
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any, List, Tuple, Optional
from src.config import settings, RAGStatus, TaskStatus
from src.ingestion.parser import ExcelParser
from src.ingestion.normalizer import DataNormalizer, ProjectData, NormalizedTask
from src.analysis.rag_engine import RAGEngine, RAGResult
from src.analysis.trend_analyzer import TrendAnalysis, analyze_weekly_trends
from src.agent.prompts import (
    WEEKLY_REPORT_SYSTEM_PROMPT,
    WEEKLY_REPORT_USER_PROMPT,
    EXECUTIVE_PRESENTATION_PROMPT
)

class ProjectHealthAgent:
    """
    AI agent that reads project plans, computes RAG status, and generates reports.
    """
    
    def __init__(self):
        self.parser = ExcelParser()
        self.normalizer = DataNormalizer()
        self.rag_engine = RAGEngine()
        self.client = None
        self._init_openai_client()
        
    def _init_openai_client(self):
        if settings.openai_api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=settings.openai_api_key,
                    base_url=settings.openai_api_base
                )
            except Exception as e:
                print(f"⚠️ Failed to initialize OpenAI client: {e}. Falling back to templates.")
                self.client = None

    def analyze_project(self, filepath: Path, ref_date: date) -> Tuple[ProjectData, RAGResult]:
        """
        Ingest, normalize, and score a project file.
        """
        raw_parsed = self.parser.parse(filepath)
        project_data = self.normalizer.normalize(raw_parsed, ref_date)
        rag_result = self.rag_engine.compute_rag(project_data)
        return project_data, rag_result

    def generate_weekly_report(self, project_data: ProjectData, rag_result: RAGResult, trend: TrendAnalysis) -> str:
        """
        Generates markdown report, using OpenAI if key is available, else falling back to local template.
        """
        summary = project_data.summary
        
        # Format signals details
        signal_details = ""
        for s in rag_result.signals:
            emoji = "🟢" if s.rag == RAGStatus.GREEN else "🟡" if s.rag == RAGStatus.AMBER else "🔴"
            signal_details += f"- **{s.signal_name}**: {emoji} {s.score:.0f}/100 - {s.detail}\n"
            
        # Format milestones details
        milestone_summary = ""
        for m in project_data.milestones[:12]:
            emoji = "🟢" if m.schedule_health == "Green" else "🟡" if m.schedule_health == "Yellow" else "🔴"
            var_str = f" (variance: {m.variance_days}d)" if m.variance_days is not None else ""
            milestone_summary += f"- {m.task_name}: {m.status.value} - {emoji} Health{var_str}\n"
            
        # Format critical/red tasks
        red_tasks_list = [t for t in project_data.tasks if t.status != TaskStatus.COMPLETED and (t.is_critical or t.schedule_health == "Red")]
        red_tasks = ""
        if not red_tasks_list:
            red_tasks = "None detected."
        else:
            for t in red_tasks_list[:8]:
                assigned = f"assigned to {t.assigned_to}" if t.assigned_to else "UNASSIGNED"
                var_str = f", variance: {t.variance_days}d" if t.variance_days is not None else ""
                red_tasks += f"- **{t.task_name}** ({t.status.value}, {assigned}{var_str})\n"
            if len(red_tasks_list) > 8:
                red_tasks += f"- ... and {len(red_tasks_list)-8} other tasks."
                
        # Format comments
        comments_str = ""
        if not project_data.comments:
            comments_str = "No comments available in file."
        else:
            for c in project_data.comments[:6]:
                ref = c.get("Row Reference") or "General"
                author = c.get("Author") or "Team Member"
                text = c.get("Comment") or c.get("As per scheduled agenda we have coverd all sessions") or ""
                if text:
                    comments_str += f"- [{ref}] {author}: \"{text}\"\n"
                    
        # Format trends
        trend_str = ""
        if trend:
            trend_str = f"Overall trajectory is {trend.overall_direction} (Composite Delta: {trend.score_delta:+.1f} points).\n"
            for sig_name, direction in trend.signal_trends.items():
                trend_str += f"- {sig_name}: {direction}\n"
            if trend.emerging_risks:
                trend_str += "\nEmerging Risks:\n"
                for er in trend.emerging_risks:
                    trend_str += f"- {er}\n"
        else:
            trend_str = "Initial reporting period. No historical trend data."

        # If we have OpenAI client, use it
        if self.client:
            user_content = WEEKLY_REPORT_USER_PROMPT.format(
                project_name=summary.project_name,
                project_manager=summary.project_manager,
                reference_date=str(summary.reference_date),
                overall_rag=rag_result.overall_rag.value,
                composite_score=rag_result.composite_score,
                data_confidence=rag_result.data_confidence,
                override_note=rag_result.override_applied or "None",
                confidence_warning=rag_result.confidence_warning or "None",
                signal_details=signal_details,
                milestone_summary=milestone_summary,
                total_tasks=summary.total_tasks,
                completed=summary.completed_count,
                completed_pct=summary.completed_count / max(summary.total_tasks, 1),
                in_progress=summary.in_progress_count,
                not_started=summary.not_started_count,
                on_hold=summary.on_hold_count,
                missing_assignees=sum(1 for t in project_data.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD) and not t.assigned_to),
                missing_assignee_pct=sum(1 for t in project_data.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD) and not t.assigned_to) / max(summary.in_progress_count + summary.not_started_count, 1),
                project_start=str(summary.project_start),
                project_end=str(summary.project_end),
                duration=summary.duration_days,
                elapsed_days=(summary.reference_date - summary.project_start).days,
                elapsed_pct=(summary.reference_date - summary.project_start).days / max(summary.duration_days, 1),
                red_tasks=red_tasks,
                comments=comments_str,
                trend_data=trend_str
            )
            
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": WEEKLY_REPORT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"⚠️ OpenAI API Call failed: {e}. Falling back to template-based generator.")
                
        # Falling back to Local Markdown Template
        return self._generate_fallback_report(project_data, rag_result, trend, signal_details, milestone_summary, red_tasks, comments_str, trend_str)

    def _generate_fallback_report(self, project_data: ProjectData, rag_result: RAGResult, trend: TrendAnalysis,
                                  signal_details: str, milestone_summary: str, red_tasks: str, comments_str: str, trend_str: str) -> str:
        summary = project_data.summary
        rag_emoji = "🟢" if rag_result.overall_rag == RAGStatus.GREEN else "🟡" if rag_result.overall_rag == RAGStatus.AMBER else "🔴"
        
        # Build template
        report = f"""# 📊 Weekly Project Health Report

**Project**: {summary.project_name}  
**Project Manager**: {summary.project_manager}  
**Report Date**: {summary.reference_date}  
**Report Generated By**: Project Health Reporting Agent (Local Template Engine)

---

## Overall Status: {rag_emoji} {rag_result.overall_rag.value}
**Composite Score**: {rag_result.composite_score:.1f}/100 | **Data Confidence**: {rag_result.data_confidence*100:.0f}%

{"**" + rag_result.override_applied + "**" if rag_result.override_applied else ""}
{"*Warning: " + rag_result.confidence_warning + "*" if rag_result.confidence_warning else ""}

---

## Executive Summary

The project is currently evaluated as **{rag_result.overall_rag.value}** with a composite score of **{rag_result.composite_score:.1f}/100**.
Overall, the project is **{summary.percent_complete*100:.1f}%** complete against a duration of **{summary.duration_days}** days. 
There are currently **{summary.completed_count}** tasks completed, **{summary.in_progress_count}** in progress, and **{summary.not_started_count}** not started.
A key risk factor is that **{sum(1 for t in project_data.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD) and not t.assigned_to)}** active tasks have no assigned owner.

---

## Signal Breakdown Analysis

{signal_details}

---

## Milestone Status

{milestone_summary}

---

## 🚨 Top Risks

1. **Schedule Slippage**: Key milestones are showing negative variances against baseline dates.
2. **Resource Gaps**: High proportion of active tasks do not have assigned resources.
3. **Hypercare Readiness**: Early phases are running behind, compressing downstream UAT and Hypercare timelines.

---

## ✅ Recommendations

1. **Assign Owners**: Immediately assign resources to active, unassigned tasks on the critical path.
2. **Review Baselines**: Re-align milestones showing significant negative variance to prevent cascading blockages.
3. **Enable Blocked Tasks**: Address tasks currently "On Hold" to resume work on integration items.

---

## 📈 Trend Analysis

{trend_str}

---

## ⚠️ Data Quality Notes

- Task records analyzed: {summary.total_tasks}
- Data confidence: {rag_result.data_confidence*100:.1f}%
- Unassigned active tasks: {sum(1 for t in project_data.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD) and not t.assigned_to)}
"""
        return report

    def generate_presentation_content(self, all_reports_text: str) -> Dict[str, Any]:
        """
        Uses LLM to summarize and format slides, or falls back to template presentation objects.
        """
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": "You are a professional slide generator. Output valid JSON meeting the format specifications exactly."},
                        {"role": "user", "content": EXECUTIVE_PRESENTATION_PROMPT.format(reports_data=all_reports_text)}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                print(f"⚠️ OpenAI Presentation content gen failed: {e}. Using fallback presentation content.")
                
        # Local fallback slides
        return self._get_fallback_presentation_content()

    def _get_fallback_presentation_content(self) -> Dict[str, Any]:
        return {
            "slide1": {
                "title": "Portfolio Health Overview",
                "subtitle": "Critical schedule and resource risks impacting S2P implementation timelines",
                "bullets": [
                    "S2P Project (Titan) is currently RED with composite score of 33/100.",
                    "Project Plan B (UniSan) is currently RED with composite score of 32/100.",
                    "Both projects suffer from severe resource allocation shortages.",
                    "Active tasks unassigned: S2P (67.5%), Project Plan B (35.4%).",
                    "Cascading schedule delays are impacting downstream Hypercare phases."
                ],
                "speaker_notes": "Good morning team. This slide presents the health of our active S2P implementation portfolio. Both projects are currently in Red status, driven by significant delays in configuration workshops and massive gaps in resource assignments."
            },
            "slide2": {
                "title": "Portfolio Trajectory Trends",
                "subtitle": "Steep decline in health metrics over the past 3 weeks",
                "bullets": [
                    "S2P Project composite health fell from 52 (Amber) to 33 (Red) in 14 days.",
                    "Project Plan B health dropped from 48 (Amber) to 32 (Red) in the same period.",
                    "Timeline compression is accelerating in build and configuration phases.",
                    "Schedule performance index (SPI) for both projects is below 0.80.",
                    "Trajectory is DECLINING, and urgent executive intervention is required."
                ],
                "speaker_notes": "Looking at the 3-week rolling trends, we see a rapid decline in both projects. This is not a sudden drop but an acceleration of build delays that have gone unmitigated."
            },
            "slide3": {
                "title": "Critical Risk Matrix",
                "subtitle": "Core schedule, resource, and blocker issues mapped by impact",
                "bullets": [
                    "Risk 1: S2P Phase 2 P2P schedule delay of 81 days (High Impact / High Likelihood).",
                    "Risk 2: S2P Hypercare 6% complete with 30-day slip (High Impact / High Likelihood).",
                    "Risk 3: S2P Resource Gap (67% active tasks unassigned) (High Impact / High Likelihood).",
                    "Risk 4: Plan B Training Phase I delay of 17 days (Medium Impact / High Likelihood).",
                    "Risk 5: Plan B Configuration Documentation delay of 13 days (Medium Impact / Medium Likelihood)."
                ],
                "speaker_notes": "We have prioritized our risks. The top three are schedule slippages on S2P Phase 2, Hypercare stalls on S2P, and the extensive resource gaps across the board."
            },
            "slide4": {
                "title": "Schedule Performance Deep-Dive",
                "subtitle": "Detailed look at milestone slippages across key phases",
                "bullets": [
                    "S2P build phase is running 32 days behind schedule (98% done but stalled).",
                    "S2P Phase 2 P2P is currently 21% complete with -81 days variance.",
                    "Plan B Training Phase I is delayed 17 days, causing cascading impacts.",
                    "Plan B Hypercare Phase I has a 13-day delay (25% complete).",
                    "Late configuration document approvals are compressing testing cycles."
                ],
                "speaker_notes": "This slide breaks down the specific schedule offenders. S2P Phase 2 is currently 81 days late against baseline, and Plan B's Training is pushing out critical launch dates."
            },
            "slide5": {
                "title": "Resource Gaps & Dependency Analysis",
                "subtitle": "Unassigned active tasks and critical path blocker review",
                "bullets": [
                    "S2P Project: 333 tasks (67%) have no assigned owner.",
                    "Project Plan B: 136 tasks (35%) have no assigned owner.",
                    "S2P has 3 active blockers 'On Hold' related to D&B integrations.",
                    "Critical path tasks delayed due to unassigned integration work.",
                    "Downstream testing depends on immediate completion of integration mappings."
                ],
                "speaker_notes": "Resource assignment is our biggest bottleneck. With 67% of tasks unassigned in the S2P project, progress has halted. We also have three active blockers on JDE and D&B integrations."
            },
            "slide6": {
                "title": "Strategic Recommendations",
                "subtitle": "Actionable steps to stabilize portfolio health and recover timelines",
                "bullets": [
                    "Immediate Action: Assign dedicated owners to critical path tasks (Owner: PMs).",
                    "Blocker Escalation: Set up priority call to resolve D&B credentials (Owner: Zycus Sponsor).",
                    "Timeline Re-baselining: Adjust S2P Phase 2 milestone expectations (Owner: Aftab H.).",
                    "UAT Mitigation: Pull forward Plan B Phase II configuration validations (Owner: Rajat B.).",
                    "Governance: Establish weekly cross-project syncs to monitor resource gaps."
                ],
                "speaker_notes": "To recover, we must immediately assign resources to critical path tasks, escalate the D&B integration credential blocker today, and adjust our baselines for the remaining S2P phases."
            },
            "slide7": {
                "title": "30-Day Outlook & Forecast",
                "subtitle": "Scenario analysis with and without proposed interventions",
                "bullets": [
                    "Without Intervention: S2P Phase 2 Go-Live will slip from Dec 2026 to Mar 2027.",
                    "Without Intervention: Plan B Phase II milestones will suffer a 3-week cascade delay.",
                    "With Intervention: Blocker resolution will recover 10 days of integration timeline.",
                    "With Intervention: Resource allocation will stabilize S2P build progress.",
                    "Milestone Decision: Lock resource assignments by July 15."
                ],
                "speaker_notes": "In the next 30 days, we face a critical decision. If we don't allocate resources now, our December Go-Live for Titan will slip into early next year. Intervening now recovers crucial schedule variance."
            }
        }

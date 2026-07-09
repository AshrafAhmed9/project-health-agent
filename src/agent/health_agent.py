import json
from pathlib import Path
from datetime import date
from typing import Dict, Any, Tuple
from src.config import settings, RAGStatus, TaskStatus
from src.ingestion.parser import ExcelParser
from src.ingestion.normalizer import DataNormalizer, ProjectData
from src.analysis.rag_engine import RAGEngine, RAGResult
from src.analysis.trend_analyzer import TrendAnalysis
from src.agent.prompts import (
    WEEKLY_REPORT_SYSTEM_PROMPT,
    WEEKLY_REPORT_USER_PROMPT,
    EXECUTIVE_PRESENTATION_PROMPT,
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
                    api_key=settings.openai_api_key, base_url=settings.openai_api_base
                )
            except Exception as e:
                print(
                    f"⚠️ Failed to initialize OpenAI client: {e}. Falling back to templates."
                )
                self.client = None

    def analyze_project(
        self, filepath: Path, ref_date: date
    ) -> Tuple[ProjectData, RAGResult]:
        """
        Ingest, normalize, and score a project file.
        """
        raw_parsed = self.parser.parse(filepath)
        project_data = self.normalizer.normalize(raw_parsed, ref_date)
        rag_result = self.rag_engine.compute_rag(project_data)
        return project_data, rag_result

    def generate_weekly_report(
        self, project_data: ProjectData, rag_result: RAGResult, trend: TrendAnalysis
    ) -> str:
        """
        Generates markdown report, using OpenAI if key is available, else falling back to local template.
        """
        summary = project_data.summary

        # Format signals details
        signal_details = ""
        for s in rag_result.signals:
            emoji = (
                "🟢"
                if s.rag == RAGStatus.GREEN
                else "🟡" if s.rag == RAGStatus.AMBER else "🔴"
            )
            signal_details += (
                f"- **{s.signal_name}**: {emoji} {s.score:.0f}/100 - {s.detail}\n"
            )

        # Format milestones details
        milestone_summary = ""
        for m in project_data.milestones[:12]:
            emoji = (
                "🟢"
                if m.schedule_health == "Green"
                else "🟡" if m.schedule_health == "Yellow" else "🔴"
            )
            var_str = (
                f" (variance: {m.variance_days}d)"
                if m.variance_days is not None
                else ""
            )
            milestone_summary += (
                f"- {m.task_name}: {m.status.value} - {emoji} Health{var_str}\n"
            )

        # Format critical/red tasks
        red_tasks_list = [
            t
            for t in project_data.tasks
            if t.status != TaskStatus.COMPLETED
            and (t.is_critical or t.schedule_health == "Red")
        ]
        red_tasks = ""
        if not red_tasks_list:
            red_tasks = "None detected."
        else:
            for t in red_tasks_list[:8]:
                assigned = (
                    f"assigned to {t.assigned_to}" if t.assigned_to else "UNASSIGNED"
                )
                var_str = (
                    f", variance: {t.variance_days}d"
                    if t.variance_days is not None
                    else ""
                )
                red_tasks += (
                    f"- **{t.task_name}** ({t.status.value}, {assigned}{var_str})\n"
                )
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
                text = (
                    c.get("Comment")
                    or c.get("As per scheduled agenda we have coverd all sessions")
                    or ""
                )
                if text:
                    comments_str += f'- [{ref}] {author}: "{text}"\n'

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
                missing_assignees=sum(
                    1
                    for t in project_data.tasks
                    if t.status
                    in (
                        TaskStatus.IN_PROGRESS,
                        TaskStatus.NOT_STARTED,
                        TaskStatus.ON_HOLD,
                    )
                    and not t.assigned_to
                ),
                missing_assignee_pct=sum(
                    1
                    for t in project_data.tasks
                    if t.status
                    in (
                        TaskStatus.IN_PROGRESS,
                        TaskStatus.NOT_STARTED,
                        TaskStatus.ON_HOLD,
                    )
                    and not t.assigned_to
                )
                / max(summary.in_progress_count + summary.not_started_count, 1),
                project_start=str(summary.project_start),
                project_end=str(summary.project_end),
                duration=summary.duration_days,
                elapsed_days=(summary.reference_date - summary.project_start).days,
                elapsed_pct=(summary.reference_date - summary.project_start).days
                / max(summary.duration_days, 1),
                red_tasks=red_tasks,
                comments=comments_str,
                trend_data=trend_str,
            )

            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {"role": "system", "content": WEEKLY_REPORT_SYSTEM_PROMPT},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.2,
                )
                return response.choices[0].message.content
            except Exception as e:
                print(
                    f"⚠️ OpenAI API Call failed: {e}. Falling back to template-based generator."
                )

        # Falling back to Local Markdown Template
        return self._generate_fallback_report(
            project_data,
            rag_result,
            trend,
            signal_details,
            milestone_summary,
            red_tasks,
            comments_str,
            trend_str,
        )

    def _generate_fallback_report(
        self,
        project_data: ProjectData,
        rag_result: RAGResult,
        trend: TrendAnalysis,
        signal_details: str,
        milestone_summary: str,
        red_tasks: str,
        comments_str: str,
        trend_str: str,
    ) -> str:
        summary = project_data.summary
        rag_emoji = (
            "🟢"
            if rag_result.overall_rag == RAGStatus.GREEN
            else "🟡" if rag_result.overall_rag == RAGStatus.AMBER else "🔴"
        )

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

    def generate_presentation_content(
        self, all_reports_text: str, portfolio: list = None
    ) -> Dict[str, Any]:
        """
        Uses LLM to summarize and format slides, or falls back to a deterministic
        generator that derives slide content from the computed portfolio metrics.
        `portfolio` is a list of dicts: {"project_data", "latest" RAGResult,
        "history" [RAGResult oldest->newest], "weeks" [str]}.
        """
        slide_content = None
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=settings.openai_model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a professional slide generator. Output valid JSON meeting the format specifications exactly.",
                        },
                        {
                            "role": "user",
                            "content": EXECUTIVE_PRESENTATION_PROMPT.format(
                                reports_data=all_reports_text
                            ),
                        },
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2,
                )
                slide_content = json.loads(response.choices[0].message.content)
            except Exception as e:
                print(
                    f"⚠️ OpenAI Presentation content gen failed: {e}. Using fallback presentation content."
                )

        if slide_content is None:
            slide_content = self._build_data_driven_slides(portfolio)

        # Always attach deterministic visual extras (stat cards + risk matrix)
        # computed from the actual data so slide visuals never drift from reality.
        if portfolio:
            slide_content["project_cards"] = self._build_project_cards(portfolio)
            slide_content["risk_matrix"] = self._build_risk_matrix(portfolio)
        return slide_content

    # ------------------------------------------------------------------
    # Deterministic (offline) presentation content, derived from real data
    # ------------------------------------------------------------------

    @staticmethod
    def _trim(text: str, limit: int) -> str:
        """Truncate at a word boundary with an ellipsis instead of mid-word."""
        text = (text or "").strip()
        if len(text) <= limit:
            return text
        cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:")
        return cut + "…"

    @staticmethod
    def _project_stats(entry: Dict[str, Any]) -> Dict[str, Any]:
        """Compute the key display metrics for one portfolio project."""
        proj_data = entry["project_data"]
        latest = entry["latest"]
        summary = proj_data.summary

        active = [
            t
            for t in proj_data.tasks
            if t.status
            in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)
        ]
        unassigned = sum(1 for t in active if not t.assigned_to)
        unassigned_pct = unassigned / max(len(active), 1)

        # Use the SPI computed by the schedule analyzer so every surface
        # (report, card, slide) quotes the same number.
        import re

        spi = None
        for s in latest.signals:
            if "schedule" in s.signal_name.lower():
                match = re.search(r"SPI\s*=\s*(\d+(?:\.\d+)?)", s.detail or "")
                if match:
                    spi = float(match.group(1))
                break
        if spi is None:
            elapsed = (summary.reference_date - summary.project_start).days
            elapsed_ratio = elapsed / max(summary.duration_days, 1)
            spi = (
                summary.percent_complete / elapsed_ratio if elapsed_ratio > 0 else None
            )

        history = entry.get("history") or [latest]
        first_score = history[0].composite_score
        delta = latest.composite_score - first_score

        signal_map = {s.signal_name: s for s in latest.signals}
        weak_signals = sorted(
            (s for s in latest.signals if s.score <= 60), key=lambda s: s.score
        )
        slipped_milestones = sorted(
            (
                m
                for m in proj_data.milestones
                if m.status != TaskStatus.COMPLETED
                and m.variance_days is not None
                and m.variance_days < 0
            ),
            key=lambda m: m.variance_days,
        )

        return {
            "name": summary.project_name,
            "pm": summary.project_manager,
            "rag": latest.overall_rag.value,
            "score": latest.composite_score,
            "first_score": first_score,
            "delta": delta,
            "pct_complete": summary.percent_complete,
            "spi": spi,
            "active": len(active),
            "unassigned": unassigned,
            "unassigned_pct": unassigned_pct,
            "on_hold": summary.on_hold_count,
            "confidence": latest.data_confidence,
            "signals": signal_map,
            "weak_signals": weak_signals,
            "slipped_milestones": slipped_milestones,
        }

    def _build_project_cards(self, portfolio: list) -> list:
        cards = []
        for entry in portfolio:
            st = self._project_stats(entry)
            emoji = {"GREEN": "🟢", "AMBER": "🟡", "RED": "🔴"}.get(st["rag"], "⚪")
            spi_str = f"{st['spi']:.2f}" if st["spi"] is not None else "N/A"
            cards.append(
                {
                    "title": st["name"],
                    "lines": [
                        f"Overall Status: {emoji} {st['rag']} ({st['score']:.0f}/100)",
                        f"Completion: {st['pct_complete']*100:.0f}%",
                        f"Schedule Index (SPI): {spi_str}",
                        f"Unassigned active tasks: {st['unassigned']} ({st['unassigned_pct']*100:.0f}%)",
                        f"Data confidence: {st['confidence']*100:.0f}%",
                    ],
                }
            )
        return cards

    def _build_risk_matrix(self, portfolio: list) -> Dict[str, list]:
        matrix = {"high_high": [], "high_med": [], "med_med": []}
        for entry in portfolio:
            st = self._project_stats(entry)
            short = st["name"].split("-")[-1].strip()
            for s in st["weak_signals"]:
                item = f"{short}: {s.signal_name} ({s.score:.0f}/100)"
                if s.score < 40:
                    matrix["high_high"].append(item)
                elif s.score < 55:
                    matrix["high_med"].append(item)
                else:
                    matrix["med_med"].append(item)
            for m in st["slipped_milestones"][:2]:
                item = f"{short}: {self._trim(m.task_name, 30)} ({m.variance_days}d)"
                if m.variance_days <= -30:
                    matrix["high_high"].append(item)
                elif m.variance_days <= -10:
                    matrix["high_med"].append(item)
        # Cap each quadrant so the visual stays readable
        return {k: v[:3] for k, v in matrix.items()}

    def _build_data_driven_slides(self, portfolio: list) -> Dict[str, Any]:
        """Build the 7-slide executive deck content from computed metrics."""
        if not portfolio:
            raise ValueError(
                "No portfolio data supplied for offline presentation generation."
            )

        stats = [self._project_stats(e) for e in portfolio]
        weeks = portfolio[0].get("weeks") or []
        period = f"{weeks[0]} to {weeks[-1]}" if weeks else "the reporting period"

        def direction(delta):
            if delta > 3:
                return "IMPROVING"
            if delta < -3:
                return "DECLINING"
            return "STABLE"

        # --- Slide 1: Portfolio overview -------------------------------
        s1_bullets = []
        for st in stats:
            s1_bullets.append(
                f"{st['name']} is {st['rag']} with a composite health score of "
                f"{st['score']:.0f}/100 ({st['pct_complete']*100:.0f}% complete)."
            )
        worst_resource = max(stats, key=lambda s: s["unassigned_pct"])
        s1_bullets.append(
            "Resource coverage is the portfolio's weakest signal: "
            + ", ".join(
                f"{st['unassigned_pct']*100:.0f}% of {st['name'].split('-')[-1].strip()} active tasks are unassigned"
                for st in stats
            )
            + "."
        )
        s1_bullets.append(
            f"Combined, {sum(st['unassigned'] for st in stats)} active tasks across the portfolio have no owner, "
            f"led by {worst_resource['name']}."
        )
        s1_bullets.append(
            "Both projects carry schedule slippage on in-flight phases that is compressing downstream UAT and Hypercare windows."
        )

        # --- Slide 2: Trends --------------------------------------------
        s2_bullets = []
        for st in stats:
            s2_bullets.append(
                f"{st['name']}: composite score moved from {st['first_score']:.0f} to {st['score']:.0f} "
                f"({st['delta']:+.1f} pts) over {period} — trajectory {direction(st['delta'])}."
            )
        avg_delta = sum(st["delta"] for st in stats) / len(stats)
        s2_bullets.append(
            f"Portfolio-average health changed {avg_delta:+.1f} points over the period; "
            f"overall trajectory is {direction(avg_delta)}."
        )
        s2_bullets.append(
            "Score erosion is driven primarily by schedule performance and growing critical-path delays, not by task velocity."
        )

        # --- Slide 3: Risk matrix ---------------------------------------
        s3_bullets = []
        rank = 1
        for st in stats:
            for s in st["weak_signals"][:2]:
                s3_bullets.append(
                    f"Risk {rank}: {st['name'].split('-')[-1].strip()} — {s.signal_name} scored {s.score:.0f}/100. {self._trim(s.detail, 95)}"
                )
                rank += 1
            if st["slipped_milestones"]:
                m = st["slipped_milestones"][0]
                s3_bullets.append(
                    f"Risk {rank}: {st['name'].split('-')[-1].strip()} — milestone '{m.task_name}' is {abs(m.variance_days)} days behind baseline."
                )
                rank += 1
        s3_bullets = s3_bullets[:5]

        # --- Slide 4: Schedule deep-dive --------------------------------
        s4_bullets = []
        for st in stats:
            sched = next(
                (s for s in st["signals"].values() if "schedule" in s.signal_name.lower()),
                None,
            )
            if sched:
                s4_bullets.append(
                    f"{st['name'].split('-')[-1].strip()}: schedule signal {sched.score:.0f}/100 — {self._trim(sched.detail, 115)}"
                )
            for m in st["slipped_milestones"][:2]:
                s4_bullets.append(
                    f"{st['name'].split('-')[-1].strip()}: '{m.task_name}' running {abs(m.variance_days)} days behind baseline ({m.status.value})."
                )
        s4_bullets = s4_bullets[:6]

        # --- Slide 5: Resources & dependencies --------------------------
        s5_bullets = []
        for st in stats:
            s5_bullets.append(
                f"{st['name'].split('-')[-1].strip()}: {st['unassigned']} of {st['active']} active tasks "
                f"({st['unassigned_pct']*100:.0f}%) have no assigned owner; {st['on_hold']} tasks are On Hold."
            )
            dep = next(
                (s for s in st["signals"].values() if "dependency" in s.signal_name.lower()),
                None,
            )
            if dep:
                s5_bullets.append(
                    f"{st['name'].split('-')[-1].strip()}: dependency risk {dep.score:.0f}/100 — {self._trim(dep.detail, 105)}"
                )
        s5_bullets = s5_bullets[:6]

        # --- Slide 6: Recommendations ------------------------------------
        rec_map = [
            ("resource", "Assign dedicated owners to all unassigned critical-path tasks within one week (Owner: Project Managers)."),
            ("schedule", "Re-baseline milestones with material negative variance and publish a recovery plan (Owner: Delivery Leads)."),
            ("blocker", "Escalate all 'On Hold' blockers to the executive sponsor for resolution this cycle (Owner: Sponsor)."),
            ("dependency", "Protect the critical path: expedite delayed predecessor tasks and add float buffers (Owner: PMO)."),
            ("milestone", "Introduce mid-phase checkpoint reviews for milestones trending late (Owner: PMO)."),
        ]
        weak_names = {
            s.signal_name.lower() for st in stats for s in st["weak_signals"]
        }
        s6_bullets = [
            rec for key, rec in rec_map if any(key in n for n in weak_names)
        ]
        s6_bullets.append(
            "Governance: establish a weekly cross-project health review using this automated report."
        )
        s6_bullets = s6_bullets[:5]

        # --- Slide 7: Outlook --------------------------------------------
        s7_bullets = []
        for st in stats:
            n_weeks = max(len(portfolio[0].get("weeks") or [1, 2]) - 1, 1)
            weekly_delta = st["delta"] / n_weeks
            projected = st["score"] + weekly_delta * 4
            s7_bullets.append(
                f"{st['name'].split('-')[-1].strip()}: at the current trend ({weekly_delta:+.1f} pts/week), "
                f"the composite score is projected at ~{projected:.0f}/100 in 30 days"
                + (
                    " — crossing into RED territory without intervention."
                    if projected < 40 <= st["score"]
                    else "."
                )
            )
        s7_bullets.append(
            "With intervention (owner assignment + blocker escalation), resource and blocker signals can recover within two reporting cycles."
        )
        s7_bullets.append(
            "Decision required: lock resource assignments and approve re-baselined milestones at the next steering committee."
        )

        def notes(text):
            return text

        return {
            "slide1": {
                "title": "Portfolio Health Overview",
                "subtitle": f"Automated RAG assessment across {len(stats)} active implementations ({period})",
                "bullets": s1_bullets[:5],
                "speaker_notes": notes(
                    "This slide summarizes the automated health assessment of the portfolio. "
                    + " ".join(s1_bullets[:2])
                ),
            },
            "slide2": {
                "title": "Portfolio Trajectory Trends",
                "subtitle": "Composite health score movement across the reporting period",
                "bullets": s2_bullets[:5],
                "speaker_notes": notes(
                    "Trend view across the reporting weeks. " + s2_bullets[-1]
                ),
            },
            "slide3": {
                "title": "Critical Risk Matrix",
                "subtitle": "Top risks ranked by signal severity and milestone slippage",
                "bullets": s3_bullets,
                "speaker_notes": notes(
                    "Risks are ranked from the weakest computed signals and the largest milestone variances."
                ),
            },
            "slide4": {
                "title": "Schedule Performance Deep-Dive",
                "subtitle": "Milestone slippage and schedule signal detail by project",
                "bullets": s4_bullets,
                "speaker_notes": notes(
                    "Detailed schedule breakdown, generated from baseline-versus-actual variance in the project plans."
                ),
            },
            "slide5": {
                "title": "Resource Gaps & Dependency Analysis",
                "subtitle": "Ownership coverage and critical-path exposure",
                "bullets": s5_bullets,
                "speaker_notes": notes(
                    "Resource coverage is the portfolio's most consistent weakness; the donut chart shows assigned versus unassigned active tasks."
                ),
            },
            "slide6": {
                "title": "Strategic Recommendations",
                "subtitle": "Actions mapped to the weakest health signals",
                "bullets": s6_bullets,
                "speaker_notes": notes(
                    "Each recommendation maps directly to a failing or weak signal in the RAG framework."
                ),
            },
            "slide7": {
                "title": "30-Day Outlook & Forecast",
                "subtitle": "Trend-based projection with and without intervention",
                "bullets": s7_bullets[:5],
                "speaker_notes": notes(
                    "Projection extrapolates the observed weekly score trend forward four weeks."
                ),
            },
        }

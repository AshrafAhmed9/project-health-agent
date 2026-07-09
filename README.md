# Project Health Reporting Agent

An automated pipeline designed for the Zycus AI Engineer Intern Technical Assignment. The system parses project plans, determines Red/Amber/Green (RAG) health status using a deterministic multi-signal framework, provides narrative reasoning (with LLM or offline template fallback), and generates executive slide decks.

---

## Quick Start (One-Command Run)

A launcher script is provided to handle virtual environment creation, package installation, and execution of the complete pipeline.

```bash
# From the repository root
chmod +x run.sh && ./run.sh
```

### Manual Execution

To run steps individually:

```bash
# 1. Activate the environment
source .venv/bin/activate

# 2. Run the quantitative status dashboard
python -m src.main analyze

# 3. Generate weekly reports
python -m src.main report

# 4. Generate monthly PowerPoint presentation
python -m src.main presentation

# 5. Run the complete pipeline (recommended)
python -m src.main full-run
```

### Bonus: Weekly Schedule

The agent can run unattended on a weekly cadence (every Monday at 9:00 AM) via APScheduler:

```bash
python -m src.main schedule-task
```

The scheduler re-analyzes every project plan in `data/` and writes a fresh dated report folder under `outputs/weekly_reports/`. In production this same entry point can be triggered by cron or a CI workflow instead.

### Optional: LLM-Generated Narratives

By default the system runs fully offline using a deterministic template engine. To enable LLM-written narratives and slide content, copy `.env.example` to `.env` and set `OPENAI_API_KEY` (the RAG status itself is always computed deterministically — the LLM only writes the prose):

```bash
cp .env.example .env   # then add your API key
```

---

## Deliverables Mapping

| Deliverable | File Path / Location | Description |
| :--- | :--- | :--- |
| **One-page RAG methodology** | [`rag_methodology.md`](rag_methodology.md) | Defines the mathematical signals, overrides, and assumptions of the status engine. |
| **Project Code** | [`src/`](src/) | Complete Python package containing ingestion, scoring, charting, and presentation modules. |
| **Simulated Weekly Outputs** | [`outputs/weekly_reports/`](outputs/weekly_reports/) | Reports across 3 historical weeks (`2026-06-18`, `2026-06-25`, `2026-07-02`) showing trajectories. |
| **Monthly Presentation** | [`outputs/monthly_presentation/executive_deck_july_2026.pptx`](outputs/monthly_presentation/executive_deck_july_2026.pptx) | A 7-slide, 16:9 widescreen PowerPoint deck with embedded charts ready for stakeholders. |
| **Unit & Integration Tests** | [`tests/`](tests/) | Pytest files covering parser integrity, normalized data mapping, and RAG override rules. |

---

## Technical Design Decisions

1. **Deterministic RAG + LLM Reasoning**: Rather than using an LLM to guess project health (which is non-deterministic and prone to hallucination), this system computes RAG status mathematically using 6 core signals and strict override thresholds. The LLM is used strictly to synthesize these computed metrics and comments into a coherent executive summary.
2. **Offline-First Resilience**: If no `OPENAI_API_KEY` is present in the environment or `.env` file, the pipeline automatically falls back to a rule-based template engine to draft the weekly reports and slide deck content.
3. **Schema Auto-Detection**: The ingestion parser (`parser.py`) dynamically detects the schema type based on header signatures, allowing the system to process both `S2P Project.xlsx` (33 columns) and `Project Plan B.xlsx` (37 columns) without manual column mapping adjustments.
4. **Data Quality Tracking**: The normalizer calculates a data completeness score for every task and project. If critical metadata (like baseline dates) is missing or unparseable, the system reports a data confidence warning.

---

## Analytical Signals and Weights

The status engine calculates a composite score (0-100) based on the following weighted components:
- **Schedule Performance (25%)**: Computed via Schedule Performance Index ($SPI = \frac{\% \text{ Complete}}{\text{Timeline Ratio}}$) with capping penalties for severe variance.
- **Milestone Health (20%)**: Progress scores for completed and active Level-1 milestones.
- **Task Velocity (15%)**: Forecast of progress rates relative to project close targets.
- **Blocker Density (15%)**: Density of "On Hold", stalled, or flagged active tasks.
- **Resource Coverage (10%)**: Owner allocation ratio across all active tasks.
- **Dependency Risk (15%)**: Schedule buffer/float thresholds and critical path delay indicators.

---

## Automated Tests

To execute the unit and integration test suites:
```bash
source .venv/bin/activate
python -m pytest tests/ -v
```
All tests verify parsing integrity, normalized data formats, and RAG status calculation logic.

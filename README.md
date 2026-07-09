# 🏥 Project Health Reporting Agent

An AI-powered system designed for the Zycus AI Engineer Intern Technical Assignment. It automatically parses project plans, determines Red/Amber/Green (RAG) health status using a deterministic multi-signal framework, provides reasoning (with LLM or offline template fallback), and constructs slide decks for executive VPs.

---

## 🚀 Quick Start (One-Command Run)

We provide a launcher script that handles virtual environment creation, package installations, and executes the complete reporting pipeline.

```bash
# Navigate to the assignment folder
cd "/Users/ashraf/Desktop/projects/zycus assignment"

# Make launcher executable and run
chmod +x run.sh && ./run.sh
```

### Manual Execution

If you prefer to run steps individually:

```bash
# 1. Activate the environment
source .venv/bin/activate

# 2. Run the quantitative dashboard
python -m src.main analyze

# 3. Generate weekly reports
python -m src.main report

# 4. Generate monthly PowerPoint presentation
python -m src.main presentation

# 5. Run the complete pipeline (recommended)
python -m src.main full-run
```

---

## 🎨 Deliverables Mapping

| Deliverable | File Path / Location | Description |
| :--- | :--- | :--- |
| **One-page RAG methodology** | [`rag_methodology.md`](file:///Users/ashraf/Desktop/projects/zycus%20assignment/rag_methodology.md) | Defines the mathematical signals, overrides, and assumptions of the status engine. |
| **Working AI Agent Code** | [`src/`](file:///Users/ashraf/Desktop/projects/zycus%20assignment/src) | Complete Python package containing ingestion, scoring, charting, and presentation modules. |
| **Simulated Weekly Outputs** | [`outputs/weekly_reports/`](file:///Users/ashraf/Desktop/projects/zycus%20assignment/outputs/weekly_reports) | Reports across 3 historical weeks (`2026-06-18`, `2026-06-25`, `2026-07-02`) showing trajectories. |
| **Monthly Presentation** | [`outputs/monthly_presentation/executive_deck_july_2026.pptx`](file:///Users/ashraf/Desktop/projects/zycus%20assignment/outputs/monthly_presentation/executive_deck_july_2026.pptx) | A 7-slide, 16:9 widescreen PowerPoint deck with embedded charts ready for VPs. |
| **Unit Tests** | [`tests/`](file:///Users/ashraf/Desktop/projects/zycus%20assignment/tests) | Pytest files covering parser integrity and RAG override rules. |

---

## 🏗️ Design Decisions (Why This Wins)

1. **Deterministic RAG + LLM Reasoning**: Most candidates use an LLM to guess the RAG status. This is error-prone, slow, and lacks auditability. Our system separates the concerns: a **deterministic engine computes the RAG mathematically** using 6 signals and specific thresholds, while the **LLM is used only to generate the plain-English narrative**. A VP can trace a RED status to a specific formula.
2. **Offline Resilience**: The system detects if an `OPENAI_API_KEY` is present. If missing, it automatically falls back to a **local template generator** for reports and slides. The entire pipeline executes successfully offline out-of-the-box.
3. **Multi-Schema Ingestion**: The two project plans (`S2P Project.xlsx` and `Project Plan B.xlsx`) have different column counts (33 vs 37) and different name schemas (e.g., Level vs Ancestors). The ingestion parser automatically detects the header signature and maps the schemas to a unified record structure.
4. **Data Confidence Rating**: Messy data (like `#UNPARSEABLE` formulas or missing dates) is handled gracefully without crashing, and decreases a computed "Data Confidence" percentage in the report headers to notify leadership.

---

## 📊 Analytical signals used

The status engine calculates a composite score (0-100) using these weighted components:
- **Schedule Performance (25%)**: SPI calculation ($\text{SPI} = \frac{\% \text{ Complete}}{\text{Timeline Ratio}}$) + variance penalty caps for delay bounds.
- **Milestone Health (20%)**: Progress scores for completed and active Level-1 milestones.
- **Task Velocity (15%)**: Forecast of progress rates relative to project close target.
- **Blocker Density (15%)**: Density of "On Hold", stalled, or flagged active items.
- **Resource Coverage (10%)**: Ownership allocation across all active tasks.
- **Dependency Risk (15%)**: Float levels and critical path delay indicators.

---

## 🧪 Verification & Tests

To execute the unit tests:
```bash
source .venv/bin/activate
python -m pytest tests/ -v
```
All tests cover parser integrity, validation of RAG computation, and override rules.

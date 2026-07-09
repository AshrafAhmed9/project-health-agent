# 🎯 ZYCUS ASSIGNMENT — ULTRA-DETAILED EXECUTION PLAN
## Project Health Reporting Agent | AI Engineer Intern
### Candidate: Ashraf Ahmed | Deadline: 11 July 2026 EOD IST

---

> **PURPOSE OF THIS DOCUMENT**: This plan is written so that ANY AI model or developer can follow it step-by-step, with zero ambiguity, and produce a top 0.1% submission. Every file, every function, every formula, every prompt template, every slide layout is specified in full detail.

---

## TABLE OF CONTENTS
1. [Data Intelligence Report](#1-data-intelligence-report)
2. [Repository Structure](#2-repository-structure)
3. [Phase 1: RAG Methodology Document](#3-phase-1-rag-methodology-document)
4. [Phase 2: Build the Agent — Full Code Specification](#4-phase-2-build-the-agent)
5. [Phase 3: Sample Weekly Report Outputs](#5-phase-3-sample-weekly-report-outputs)
6. [Phase 4: Executive Monthly Presentation](#6-phase-4-executive-monthly-presentation)
7. [Phase 5: README and Documentation](#7-phase-5-readme-and-documentation)
8. [Verification Checklist](#8-verification-checklist)
9. [Timeline](#9-timeline)

---

## 1. DATA INTELLIGENCE REPORT

> This section documents EVERY detail about the input data so the agent builder never needs to re-read the Excel files.

### 1.1 File: `S2P Project.xlsx` — Zycus–Titan S2P Implementation

**Sheets**: `Outokumpu- S2P Project` (main), `Comments`, `Summary`

**Summary Sheet Data**:
| Field | Value |
|---|---|
| Project Name | *(empty — must handle gracefully)* |
| Project Manager | Aftab Hashambhai |
| Project Start Date | 2025-12-05 |
| Project End Date | 2026-12-07 |
| Not Started | 194 |
| In Progress | 15 |
| Completed | 255 |
| On Hold | 3 |
| At Risk | High |
| Project Stage | Configuration and Build phase |
| % Complete | 0.71 (71%) |
| Schedule Health | Green |
| Today's Date | 2026-07-02 |
| Duration | 262 days |
| Project Status | In Progress |
| Target Start/End Date, Schedule Delta, Variance fields | `#UNPARSEABLE` (formula references — handle gracefully) |

**Main Sheet Schema (33 columns)**:
| Col Index | Column Name | Data Type | Notes |
|---|---|---|---|
| 0 | Project Name | str | Often empty |
| 1 | Project Category | str | Often `#UNPARSEABLE` |
| 2 | Ancestors | int | Hierarchy level indicator (0-8) |
| 3 | Project Manager | str | "Aftab Hashambhai" |
| 4 | Level | int | Task depth: 0=project, 1=phase, 2-8=subtasks |
| 5 | Phase/Milestone | str | Values: Project Initiation, Data Gathering, Requirement Workshop, Build, Pre UAT, UAT, TTT, Migration, Go Live, Hypercare |
| 6 | At Risk? | str/bool | Only 4 tasks have `True` |
| 7 | Schedule Health | str | "Green", "Yellow", "Red" |
| 8 | Task Name | str | **Primary task identifier** |
| 9 | Status | str | "Completed", "In Progress", "Not Started", "On Hold", "Not Applicable" |
| 10 | Start Date | datetime | Planned start |
| 11 | End Date | datetime | Planned end |
| 12 | % Complete | float | 0.0 to 1.0 |
| 13 | On Hold? | bool | |
| 14 | Not Applicable? | bool | |
| 15 | Duration | str | Format: "Xd" (e.g., "262d", "1d", "0") |
| 16 | Predecessors | str | Format: "3FS +7d", "22", "10", etc. |
| 17 | Description | str | Mostly empty |
| 18 | Owner | str | Mostly empty |
| 19 | OwnerShip | str | Mostly empty |
| 20 | Priority | str | Mostly empty |
| 21 | Total Float | float | Days of schedule slack |
| 22 | Critical ? | bool/str | "True" for critical path tasks |
| 23 | Baseline Start | datetime | Original planned start |
| 24 | Baseline Finish | datetime | Original planned end |
| 25 | Variance | str | Format: "-32d", "0", "1d", "-6d" — **NEGATIVE = behind schedule** |
| 26 | Status Comment | str | Rare — only 7 tasks have comments |
| 27 | Area | str | Mostly empty |
| 28 | Comments | str | Mostly empty |
| 29 | Assigned To | str | Email addresses or role names — **333 of 493 tasks have NO assignee** |
| 30 | Start | datetime | Actual/revised start (appears same as col 10 often) |
| 31 | Finish | datetime | Actual/revised end |
| 32 | RAG | str | "Green", "Yellow", "Red" — but this is **the file's precomputed RAG**, NOT what we should use. Our agent should compute independently |

**Task Distribution**:
- Completed: 262
- In Progress: 22
- Not Started: 197
- On Hold: 3
- Not Applicable: 9
- **Total: 493 task rows**

**Schedule Health Distribution**:
- Green: 465
- Yellow: 2
- Red: 25

**Hierarchy Levels**: L0 (3), L1 (14), L2 (75), L3 (130), L4 (107), L5 (97), L6 (22), L7 (25), L8 (20)

**Critical Findings**:
- Phase 1 S2C: 92% complete, Yellow, variance -6d
- Phase 2 P2P: **21% complete, RED, variance -81d** ← CRITICAL
- Configuration & Build phase: 98% complete but RED, variance -32d
- Production & Cutover: 97%, RED, variance +15d (positive = originally finished early vs baseline)
- Hypercare: **6% complete, RED, variance -30d** ← CRITICAL
- Config Doc workshop (P2P): 25%, RED, variance -43d
- **3 tasks On Hold**: Supplier Notification template, D&B credentials, D&B App enable
- **67.5% of tasks missing assignees** (333/493)

**10 Milestones/Phases (from Phase/Milestone column)**:
1. Project Initiation — Completed
2. Data Gathering — Completed
3. Requirement Workshop — Completed
4. Build — In Progress (98%, RED, -32d variance)
5. Pre UAT — *(subtasks under Build)*
6. UAT — Completed
7. TTT — Completed
8. Migration — In Progress (97%, RED)
9. Go Live — Completed
10. Hypercare — In Progress (6%, RED, -30d variance)

**Comments Sheet (8 comments)**:
- Row 292: "Due to parallel phase 1 activities onsite workshop dates are impacted" (May 18)
- Row 292: "As per scheduled agenda we have covered all sessions" (Jun 26)
- Row 294: "OTK to provide Sample for processing... complete data will be provided by or before July 10" (Jun 26)
- Row 299: "JDE mapping is pending only" (Jun 26)
- Row 301: "JDE field mapping remain to complete for PO outbound & GR Inbound" (Jun 26)
- Row 385, 391, 411, 435: Various team coordination comments (Jun 23)

---

### 1.2 File: `Project Plan B.xlsx` — Zycus–UniSan S2P Implementation

**Sheets**: `Project Plan` (main), `Comments` (empty), `Summary`

**Summary Sheet Data**:
| Field | Value |
|---|---|
| Project Name | *(empty)* |
| Project Manager | Rajat Bothra |
| Project Start Date | 2026-02-11 |
| Project End Date | 2026-10-09 |
| Not Started | 175 |
| In Progress | 35 |
| Completed | 133 |
| On Hold | 0 |
| At Risk | High |
| Project Stage | Training Phase I |
| % Complete | 0.44 (44%) |
| Schedule Health | Red |
| Today's Date | 2026-07-02 |
| Duration | 170 days |
| Project Status | In Progress |
| Target Start/End, Schedule Delta, Variance fields | `#UNPARSEABLE` |

**Main Sheet Schema (37 columns)** — DIFFERENT FROM S2P:
| Col Index | Column Name | Data Type | Notes |
|---|---|---|---|
| 0 | No.of days Until Today | formula | `#UNPARSEABLE` — formula not preserved |
| 1 | No.of days | formula | `#UNPARSEABLE` |
| 2 | Target start date to Today | formula | `#UNPARSEABLE` |
| 3 | Project Name | str | Often empty |
| 4 | Project Category | str | `#UNPARSEABLE` |
| 5 | Ancestors | int | Hierarchy level (0-8) |
| 6 | Project Manager | str | "Rajat Bothra" |
| 7 | Phase/Milestone | str | **Mostly empty** — unlike S2P |
| 8 | Area | str | Mostly empty |
| 9 | At Risk? | str | **No tasks marked** |
| 10 | Schedule Health | str | "Green", "Yellow", "Red" |
| 11 | Task Name | str | Primary task identifier |
| 12 | Status | str | "Completed", "In Progress", "Not Started" (no On Hold) |
| 13 | % Complete | float | 0.0 to 1.0 |
| 14 | Start Date | datetime | Planned start |
| 15 | End Date | datetime | Planned end |
| 16 | Priority | str | Mostly empty |
| 17 | Owner | str | Mostly empty |
| 18 | On Hold? | bool | |
| 19 | Not Applicable? | bool | |
| 20 | Duration | str | Format: "Xd" |
| 21 | Predecessors | str | 283 tasks have predecessors |
| 22 | Total Float | float | Schedule slack |
| 23 | Critical ? | bool/str | |
| 24 | Baseline Start | datetime | Only 1 task has this |
| 25 | Baseline Finish | datetime | Only 1 task has this |
| 26 | Variance | str | **Only 1 task has this** — sparse! |
| 27 | Status Comment | str | Empty |
| 28 | Baseline Start Date | datetime | Mostly empty |
| 29 | Baseline End Date | datetime | Mostly empty |
| 30 | Comments | str | Empty |
| 31 | Assigned To | str | 136 tasks missing (35.4%) |
| 32 | Start | datetime | |
| 33 | Finish | datetime | |
| 34 | Baseline Start2 | datetime | **Second set of baselines — unique to this file** |
| 35 | Baseline Finish2 | datetime | Second baseline end |
| 36 | Variance2 | str | **Variance vs second baseline** — format: "17d", "13d", "0", "-8d" |

**IMPORTANT SCHEMA DIFFERENCES FROM S2P**:
1. Cols 0-2 are formula columns (absent in S2P) — always `#UNPARSEABLE`
2. Columns are offset by 3 positions (e.g., Task Name is col 11 not col 8)
3. Has Baseline Start2/Finish2/Variance2 (cols 34-36) — S2P doesn't have these
4. No "At Risk?" flags set
5. Phase/Milestone column is empty (phases are inferred from L1 task names)
6. Baseline cols 24-26 are almost entirely empty — use cols 34-36 instead
7. No On Hold tasks
8. Comments sheet is empty

**Task Distribution**:
- Completed: 149
- In Progress: 42
- Not Started: 192
- **Total: 383 task rows**

**Schedule Health Distribution**:
- Green: 332
- Yellow: 9
- Red: 42

**Milestone Structure (L0 and L1 tasks — 40 items)**:
| Status | Task | Health | Completion | Variance2 | Period |
|---|---|---|---|---|---|
| In Progress | Zycus - UniSan S2P Implementation (L0) | Red | 44% | -8d | Feb 11 - Oct 09 |
| Completed | Contract Sign Off | Green | 100% | 0 | Feb 11 |
| Completed | Project Initiation and Data Gathering | Green | 100% | 1d | Feb 19 - Mar 17 |
| Completed | Config Validation & Documentation (Phase I) | Green | 100% | 1d | Mar 13 - Apr 27 |
| Completed | SSO and User Integration | Green | 100% | 0 | Mar 13 - Apr 16 |
| Completed | Contract Management Basic Setup | Green | 100% | 0 | Apr 23 - May 05 |
| Completed | Supplier Info Management w/ Integration | Green | 100% | 3d | Apr 23 - May 15 |
| Completed | UAT Phase I | Green | 100% | 18d | May 04 - May 20 |
| Completed | UAT Completion I | Green | 100% | 0 | May 20 |
| Completed | Value KPI Sign-off | Green | 100% | 2d | May 18 |
| **In Progress** | **Training Phase I** | **Red** | **77%** | **17d** | May 19 - May 28 |
| Completed | Training Completion | Green | 100% | 17d | May 28 |
| Completed | Production Migration Phase I | Green | 100% | 14d | May 19 - Jun 03 |
| Completed | Go-Live Phase I | Green | 100% | 12d | Jun 08 |
| **In Progress** | **Hypercare Phase I** | **Red** | **25%** | **13d** | Jun 09 - Jul 06 |
| **In Progress** | **Config Validation & Documentation (Phase II)** | **Red** | **26%** | *missing* | Jun 19 - Jul 22 |
| **In Progress** | **eProc/eInvoice/Merlin APSD** | **Yellow** | **21%** | *missing* | Jun 19 - Aug 04 |
| In Progress | Contract Mgmt Basic Setup (Phase II) | Green | 3% | *missing* | Jul 14 - Aug 07 |
| **In Progress** | **Supplier Info Mgmt w/ Integration (Phase II)** | **Red** | **12%** | *missing* | Jun 12 - Aug 11 |
| Not Started | iSource Configuration | Green | — | *missing* | Jul 22 - Aug 06 |
| Not Started | Merlin Intake Configuration | Green | — | *missing* | Jul 22 - Aug 05 |
| Not Started | UAT Phase II | Green | — | *missing* | Aug 07 - Aug 24 |
| Not Started | Training Phase II | Green | — | *missing* | Aug 18 - Sep 02 |
| Not Started | Production Migration Phase II | Green | — | *missing* | Aug 21 - Sep 07 |
| Not Started | Go-Live Phase II | Green | — | *missing* | Sep 11 |
| Not Started | Hypercare Phase II | Green | — | *missing* | Sep 14 - Oct 09 |

---

### 1.3 Key Data Quality Issues (Agent Must Handle)

| Issue | S2P Count | Plan B Count | Handling Strategy |
|---|---|---|---|
| `#UNPARSEABLE` formula cells | ~5 per row (cols 0-2 equiv.) | ~3 per row (cols 0-2) | Skip, don't crash |
| Missing Project Name | Yes | Yes | Extract from L0 task name |
| Missing assignees | 333/493 (67.5%) | 136/383 (35.4%) | Flag as resource risk |
| Missing variance data | 221/493 (44.8%) | 382/383 (99.7%) | Compute from date comparison |
| Missing baseline dates | 221/493 | 382/383 | Use planned dates as fallback |
| Empty Phase/Milestone col | N/A (populated) | All empty | Infer from L1 task names |
| Duration format ("Xd") | All rows | All rows | Parse: strip "d", convert to int |
| Predecessor format ("3FS +7d") | Various | Various | Parse relationship type + lag |
| Missing % Complete | On Hold / Not Started tasks | Not Started tasks | Impute: Completed=1.0, Not Started=0.0, On Hold=0.0, In Progress=0.5 if missing |
| Different column schemas | 33 cols | 37 cols | Schema detection by header row |
| Empty Comments sheet | Has data | Empty | Handle gracefully |
| `None` vs empty string | Mixed | Mixed | Treat both as missing |

---

## 2. REPOSITORY STRUCTURE

> Create this exact structure. Every file listed is described in detail later.

```
zycus-project-health-agent/
│
├── README.md                                    # [Phase 5] Comprehensive documentation
├── rag_methodology.md                           # [Phase 1] One-page RAG framework
├── requirements.txt                             # Python dependencies
├── .env.example                                 # API key template
├── .gitignore                                   # Standard Python .gitignore
├── run.sh                                       # One-command launcher script
│
├── src/
│   ├── __init__.py                              # Empty
│   ├── main.py                                  # CLI entry point (typer)
│   ├── config.py                                # Pydantic settings + constants
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── parser.py                            # Excel reader + schema detection
│   │   └── normalizer.py                        # Unified ProjectData model
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── rag_engine.py                        # Deterministic RAG scoring
│   │   ├── schedule_analyzer.py                 # Schedule performance metrics
│   │   ├── milestone_tracker.py                 # Phase/milestone health
│   │   ├── blocker_detector.py                  # Blocked/on-hold detection
│   │   ├── resource_analyzer.py                 # Assignment coverage
│   │   └── trend_analyzer.py                    # Week-over-week + cross-project
│   │
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── health_agent.py                      # LangChain/OpenAI agent
│   │   └── prompts.py                           # All prompt templates
│   │
│   ├── reporting/
│   │   ├── __init__.py
│   │   ├── weekly_report.py                     # Markdown report generator
│   │   ├── presentation.py                      # python-pptx executive deck
│   │   └── charts.py                            # matplotlib chart generation
│   │
│   └── scheduler/
│       ├── __init__.py
│       └── weekly_scheduler.py                  # APScheduler cron runner
│
├── data/
│   ├── S2P Project.xlsx                         # Input file 1
│   └── Project Plan B.xlsx                      # Input file 2
│
├── outputs/
│   ├── weekly_reports/                          # Generated weekly reports
│   │   ├── 2026-06-18/                          # Simulated Week 1
│   │   │   ├── s2p_project_report.md
│   │   │   └── project_plan_b_report.md
│   │   ├── 2026-06-25/                          # Simulated Week 2
│   │   │   ├── s2p_project_report.md
│   │   │   └── project_plan_b_report.md
│   │   └── 2026-07-02/                          # Current Week 3
│   │       ├── s2p_project_report.md
│   │       └── project_plan_b_report.md
│   └── monthly_presentation/
│       └── executive_deck_july_2026.pptx        # Final 5-7 slide deck
│
└── tests/
    ├── __init__.py
    ├── test_parser.py                           # Parser unit tests
    ├── test_rag_engine.py                       # RAG calculation tests
    └── test_normalizer.py                       # Normalizer tests
```

---

## 3. PHASE 1: RAG METHODOLOGY DOCUMENT

> **File**: `rag_methodology.md`
> **Requirement**: One page defining how RAG status is determined
> **Design**: Must be clean, visual, precise — this is the FIRST thing evaluators read

### 3.1 Exact Content to Write

The document must cover ALL of the following, formatted as a professional one-pager:

#### Title
"RAG Status Methodology — Project Health Reporting Agent"

#### Section 1: Framework Overview (3-4 sentences)
Explain that we use a **Weighted Multi-Signal Composite Scoring** approach. Six independent health signals are each scored 0-100, then combined using predefined weights into a composite score that maps to Red/Amber/Green. This is NOT a pure LLM judgment — it's a deterministic, auditable algorithm with clear thresholds. The LLM layer provides plain-English reasoning on top of the quantitative scores.

#### Section 2: Signal Definitions Table

| # | Signal | Weight | What It Measures | Data Source (Columns Used) |
|---|---|---|---|---|
| 1 | Schedule Performance Index (SPI) | 25% | How actual progress compares to planned schedule. Ratio of earned schedule to planned schedule. | Planned Start/End, Actual Start/End, Baseline dates, Variance column |
| 2 | Milestone Completion Health | 20% | Whether major phases are on track vs their planned end dates. | L0-L1 tasks: Status, % Complete, End Date vs today |
| 3 | Task Completion Velocity | 15% | Whether the rate of task completion will meet the deadline at current pace. | % Complete (overall), elapsed time / total duration |
| 4 | Blocker & On-Hold Density | 15% | Quantity and severity of blocked work items. | On Hold count, At Risk flags, tasks with 0% progress past their start date |
| 5 | Resource Coverage | 10% | Whether tasks have responsible owners assigned. | Assigned To column — % of active tasks with assignees |
| 6 | Dependency & Critical Path Risk | 15% | Whether delays on predecessors will cascade. | Predecessors column, Total Float, Critical flag |

#### Section 3: Scoring Thresholds

For EACH signal, define Green/Amber/Red thresholds:

**Signal 1 — Schedule Performance Index (SPI)**:
```
SPI = (% Complete) / (Elapsed Calendar Days / Total Planned Duration)

If elapsed = 0, SPI = 1.0 (just started, no data yet)
If total duration = 0, SPI = 1.0 (milestone, no duration)

Score:
  SPI ≥ 0.95        → 100 (Green)
  0.85 ≤ SPI < 0.95 → 70  (Amber)  
  0.70 ≤ SPI < 0.85 → 40  (Amber-Red)
  SPI < 0.70         → 20  (Red)
  
Also factor in Variance column if available:
  If |variance| > 20 days behind → cap score at 30
  If |variance| > 10 days behind → cap score at 50
```

**Signal 2 — Milestone Completion Health**:
```
For each L1 milestone that should be complete by now (planned_end < today):
  - If Status = Completed → milestone_score = 100
  - If Status = In Progress and % > 90% → milestone_score = 70
  - If Status = In Progress and % ≤ 90% → milestone_score = 30
  - If Status = Not Started → milestone_score = 0

For milestones currently active (planned_start < today < planned_end):
  expected_progress = (today - planned_start) / (planned_end - planned_start)
  actual_progress = % Complete
  
  If actual ≥ expected × 0.9 → milestone_score = 90
  If actual ≥ expected × 0.7 → milestone_score = 60
  Else → milestone_score = 25

Signal Score = average(all relevant milestone scores)
```

**Signal 3 — Task Completion Velocity**:
```
elapsed_ratio = (today - project_start) / (project_end - project_start)
velocity_ratio = overall_percent_complete / elapsed_ratio

Score:
  velocity_ratio ≥ 0.95 → 100
  0.80 ≤ velocity < 0.95 → 70
  0.60 ≤ velocity < 0.80 → 40
  velocity < 0.60         → 15
```

**Signal 4 — Blocker & On-Hold Density**:
```
on_hold_count = count(tasks where Status = "On Hold")
stalled_count = count(tasks where Status = "In Progress" AND % Complete < 0.1 AND planned_start was > 14 days ago)
at_risk_count = count(tasks where At Risk = True)

total_blockers = on_hold_count + stalled_count + at_risk_count
active_tasks = count(tasks where Status in ("In Progress", "Not Started"))

blocker_ratio = total_blockers / max(active_tasks, 1)

Score:
  blocker_ratio = 0          → 100
  blocker_ratio < 0.02       → 85
  0.02 ≤ ratio < 0.05        → 60
  0.05 ≤ ratio < 0.10        → 35
  ratio ≥ 0.10               → 10
```

**Signal 5 — Resource Coverage**:
```
active_tasks = tasks where Status in ("In Progress", "Not Started")
assigned = count(active_tasks where Assigned To is not empty)
total = count(active_tasks)

coverage = assigned / max(total, 1)

Score:
  coverage ≥ 0.90 → 100
  0.70 ≤ cov < 0.90 → 70
  0.50 ≤ cov < 0.70 → 40
  cov < 0.50         → 15
```

**Signal 6 — Dependency & Critical Path Risk**:
```
critical_tasks = tasks where Critical = True
critical_delayed = count(critical_tasks where Schedule Health = "Red" OR variance < -5d)
total_critical = max(count(critical_tasks), 1)

low_float_tasks = count(tasks where Total Float < 3 and Status != "Completed")
total_active = count(active tasks)

critical_delay_ratio = critical_delayed / total_critical
low_float_ratio = low_float_tasks / max(total_active, 1)

Score:
  critical_delay_ratio = 0 AND low_float_ratio < 0.1 → 100
  critical_delay_ratio < 0.1 OR low_float_ratio < 0.2 → 70
  critical_delay_ratio < 0.3 OR low_float_ratio < 0.4 → 40
  else → 15
```

#### Section 4: Composite Score → RAG Mapping

```
composite_score = Σ (signal_score × weight) for all 6 signals

RAG Determination:
  1. If composite_score ≥ 70                    → GREEN
  2. If 40 ≤ composite_score < 70               → AMBER
  3. If composite_score < 40                     → RED

Override Rules (applied AFTER composite):
  - If ANY signal with weight ≥ 20% scores ≤ 20  → force RED
  - If ANY signal with weight ≥ 15% scores ≤ 10  → force RED  
  - If ≥ 3 signals score below 40                → force RED
  - If ≥ 2 signals score below 40                → force AMBER (min)

Data Confidence Modifier:
  data_quality = (non-missing fields) / (total expected fields)
  If data_quality < 0.5 → append "LOW CONFIDENCE" to RAG status
  If data_quality < 0.3 → status becomes "INSUFFICIENT DATA"
```

#### Section 5: Assumptions

Write these exact assumptions:
1. "Today's date" is taken from the Summary sheet's `Today's Date` field (or system date if missing)
2. Tasks with Status "Not Applicable" are excluded from all calculations
3. When baseline dates are missing, planned dates are used as the baseline
4. For Project Plan B, Variance2 (col 36) is preferred over Variance (col 26) since col 26 is nearly empty
5. Hierarchical tasks (L0-L1) represent milestones/phases; L2+ are detailed tasks
6. Missing % Complete for "In Progress" tasks is imputed as 0.5 (50%)
7. Negative variance means BEHIND schedule (e.g., -32d = 32 days late)
8. Positive variance means AHEAD of schedule or delayed start
9. The agent independently computes RAG rather than relying on the pre-existing Schedule Health column in the data

#### Section 6: Visual Diagram

Include a simple ASCII or text flowchart:
```
Excel Data → [Parser] → Normalized Tasks → [6 Signal Analyzers] → Signal Scores
                                                                        ↓
                                                            [Weighted Composite]
                                                                        ↓
                                                              RAG Status + Reasoning
```

#### Formatting Requirements for `rag_methodology.md`:
- Use clear markdown headings
- Include the signal table with thresholds
- Keep to approximately 1 page when rendered/printed (roughly 60-80 lines of content)
- Use color emoji: 🔴 🟡 🟢 for visual RAG indicators
- Professional tone — this is a consulting deliverable

---

## 4. PHASE 2: BUILD THE AGENT

### 4.1 `requirements.txt`

```
openpyxl>=3.1.0
pandas>=2.0
openai>=1.0
langchain>=0.3.0
langchain-openai>=0.3.0
python-pptx>=0.6.21
matplotlib>=3.7
apscheduler>=3.10
pydantic>=2.0
pydantic-settings>=2.0
typer>=0.9
python-dotenv>=1.0
rich>=13.0
```

### 4.2 `.env.example`

```
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o
# Optional: For local models
# OPENAI_API_BASE=http://localhost:11434/v1
# OPENAI_MODEL=llama3
```

### 4.3 `.gitignore`

```
.env
.venv/
__pycache__/
*.pyc
.DS_Store
outputs/
*.egg-info/
dist/
build/
```

### 4.4 `run.sh`

```bash
#!/bin/bash
set -e
echo "🏥 Project Health Reporting Agent"
echo "================================="

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -q -r requirements.txt

echo ""
echo "Usage:"
echo "  python -m src.main analyze          # Analyze all projects in data/"
echo "  python -m src.main report --week    # Generate weekly reports"
echo "  python -m src.main presentation     # Generate executive deck"
echo "  python -m src.main schedule         # Start weekly scheduler"
echo "  python -m src.main full-run         # Run complete pipeline"
echo ""

# Default: run full pipeline
python -m src.main full-run "$@"
```

### 4.5 `src/config.py` — FULL SPECIFICATION

```python
"""
Configuration and constants for the Project Health Agent.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from enum import Enum
from datetime import date

class RAGStatus(str, Enum):
    RED = "RED"
    AMBER = "AMBER"
    GREEN = "GREEN"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

class TaskStatus(str, Enum):
    COMPLETED = "Completed"
    IN_PROGRESS = "In Progress"
    NOT_STARTED = "Not Started"
    ON_HOLD = "On Hold"
    NOT_APPLICABLE = "Not Applicable"

# Signal weights — must sum to 1.0
SIGNAL_WEIGHTS = {
    "schedule_performance": 0.25,
    "milestone_health": 0.20,
    "task_velocity": 0.15,
    "blocker_density": 0.15,
    "resource_coverage": 0.10,
    "dependency_risk": 0.15,
}

# RAG thresholds
RAG_GREEN_THRESHOLD = 70
RAG_AMBER_THRESHOLD = 40

# Override rules
RED_OVERRIDE_SINGLE_HEAVY = 20    # If signal with weight >= 20% scores <= this → RED
RED_OVERRIDE_SINGLE_MEDIUM = 10   # If signal with weight >= 15% scores <= this → RED
RED_OVERRIDE_MULTI_COUNT = 3      # If N signals score below 40 → RED
AMBER_OVERRIDE_MULTI_COUNT = 2    # If N signals score below 40 → AMBER

# Data confidence thresholds
LOW_CONFIDENCE_THRESHOLD = 0.5
INSUFFICIENT_DATA_THRESHOLD = 0.3

class Settings(BaseSettings):
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_api_base: str = Field(default="https://api.openai.com/v1", env="OPENAI_API_BASE")
    
    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs")
    reference_date: date = date(2026, 7, 2)  # "Today" per the data files
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 4.6 `src/ingestion/parser.py` — FULL SPECIFICATION

This module must:

1. **Detect which schema** the Excel file uses:
   - If col 0 header == "Project Name" → S2P schema (33 cols)
   - If col 0 header == "No.of days Until Today" → Plan B schema (37 cols)
   
2. **Read the Summary sheet** and extract:
   - Project Manager
   - Project Start Date
   - Project End Date
   - % Complete
   - Schedule Health
   - At Risk level
   - Today's Date (use as reference date)
   - Duration
   
3. **Read the main task sheet** and for each row (skip header row):
   - Map columns to a unified `TaskRecord` dict based on detected schema
   - Handle `#UNPARSEABLE`: if any cell value == "#UNPARSEABLE" or is a string that starts with "#", set to None
   - Handle `None` vs empty string: both are treated as missing
   - Parse duration: strip "d" suffix, convert to int. Handle "0" as 0.
   - Parse dates: handle datetime objects from openpyxl (they come as `datetime.datetime`)
   - Parse variance: strip "d" suffix, handle negative values ("-32d" → -32), handle "0" → 0
   - Parse % Complete: it's already a float 0-1 from openpyxl
   - Parse predecessors: keep as string for now
   - Parse Critical flag: "True" (string) → True, else False
   
4. **Read the Comments sheet** if it has data:
   - Extract (row_reference, comment_text, author, timestamp)
   
5. **Column mapping for S2P schema** (use these EXACT indices):
   ```python
   S2P_COLUMN_MAP = {
       "project_name": 0,
       "project_category": 1,
       "ancestors": 2,
       "project_manager": 3,
       "level": 4,
       "phase_milestone": 5,
       "at_risk": 6,
       "schedule_health": 7,
       "task_name": 8,
       "status": 9,
       "start_date": 10,
       "end_date": 11,
       "percent_complete": 12,
       "on_hold": 13,
       "not_applicable": 14,
       "duration": 15,
       "predecessors": 16,
       "description": 17,
       "owner": 18,
       "total_float": 21,
       "critical": 22,
       "baseline_start": 23,
       "baseline_finish": 24,
       "variance": 25,
       "status_comment": 26,
       "comments": 28,
       "assigned_to": 29,
       "actual_start": 30,
       "actual_finish": 31,
       "rag": 32,
   }
   ```
   
6. **Column mapping for Plan B schema** (use these EXACT indices):
   ```python
   PLAN_B_COLUMN_MAP = {
       "project_name": 3,
       "project_category": 4,
       "ancestors": 5,
       "project_manager": 6,
       "phase_milestone": 7,
       "area": 8,
       "at_risk": 9,
       "schedule_health": 10,
       "task_name": 11,
       "status": 12,
       "percent_complete": 13,
       "start_date": 14,
       "end_date": 15,
       "priority": 16,
       "owner": 17,
       "on_hold": 18,
       "not_applicable": 19,
       "duration": 20,
       "predecessors": 21,
       "total_float": 22,
       "critical": 23,
       "baseline_start": 24,
       "baseline_finish": 25,
       "variance": 26,
       "status_comment": 27,
       "comments": 30,
       "assigned_to": 31,
       "actual_start": 32,
       "actual_finish": 33,
       "baseline_start_2": 34,
       "baseline_finish_2": 35,
       "variance_2": 36,
   }
   ```

7. **For Plan B**: Use `variance_2` (col 36) as the primary variance since `variance` (col 26) is almost entirely empty. If `variance_2` exists, use it; else fall back to `variance`.

8. **For Plan B**: Use `baseline_start_2` (col 34) and `baseline_finish_2` (col 35) as baselines since cols 24-25 are mostly empty.

### 4.7 `src/ingestion/normalizer.py` — FULL SPECIFICATION

Defines the unified data model and normalizes parsed data:

```python
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
    comments: list[dict]                # From Comments sheet
    source_file: str
    schema_type: str                    # "s2p" or "plan_b"
    data_quality_score: float           # Overall 0.0-1.0
```

**Normalization Logic**:
1. For each parsed task row, map to `NormalizedTask`
2. Impute missing `percent_complete`:
   - Completed → 1.0
   - Not Started → 0.0
   - On Hold → leave as-is (don't impute)
   - In Progress with None → 0.5
3. Determine `is_milestone`: True if level in (0, 1)
4. Infer `phase` for Plan B (where Phase/Milestone column is empty):
   - Walk up the hierarchy using the `ancestors`/`level` column
   - The nearest L1 parent task's name IS the phase name
   - Alternatively, for L1 tasks themselves, their task_name IS the phase name
5. Calculate `data_completeness` per task: count non-None fields / total expected fields
6. Calculate overall `data_quality_score`: mean of all tasks' data_completeness
7. Filter out tasks where `status` == "Not Applicable" and `not_applicable` == True
8. Extract project name: Use Summary sheet's Project Name; if empty, use the L0 task name

### 4.8 `src/analysis/rag_engine.py` — FULL SPECIFICATION

This is the **CORE** of the system. Implement EXACTLY the formulas from Section 3.

```python
@dataclass
class SignalResult:
    signal_name: str
    score: float                    # 0-100
    weight: float                   # 0.0-1.0
    weighted_score: float           # score × weight
    rag: RAGStatus                  # Signal-level RAG
    detail: str                     # Human-readable explanation
    raw_metrics: dict               # Underlying numbers for transparency

@dataclass
class RAGResult:
    overall_rag: RAGStatus
    composite_score: float          # 0-100
    signals: list[SignalResult]     # All 6 signals
    override_applied: str | None    # Which override rule triggered, if any
    data_confidence: float          # 0.0-1.0
    confidence_warning: str | None  # "LOW CONFIDENCE" or None
    reasoning_context: dict         # Everything the LLM needs for narrative
```

**Function**: `compute_rag(project_data: ProjectData) -> RAGResult`

Implementation steps:
1. Call each signal analyzer (schedule, milestone, velocity, blocker, resource, dependency)
2. Each returns a `SignalResult`
3. Compute `composite_score = sum(signal.weighted_score for signal in signals)`
4. Apply override rules:
   - Check if any signal with weight ≥ 0.20 has score ≤ 20 → override to RED
   - Check if any signal with weight ≥ 0.15 has score ≤ 10 → override to RED
   - Count signals with score < 40: if ≥ 3 → RED, if ≥ 2 → AMBER (at minimum)
5. Apply data confidence check
6. Build `reasoning_context` dict with all metrics for the LLM

### 4.9 `src/analysis/schedule_analyzer.py`

**Function**: `analyze_schedule(project_data: ProjectData) -> SignalResult`

```python
def analyze_schedule(project_data: ProjectData) -> SignalResult:
    summary = project_data.summary
    
    # Calculate SPI
    total_duration = (summary.project_end - summary.project_start).days
    elapsed = (summary.reference_date - summary.project_start).days
    elapsed_ratio = elapsed / max(total_duration, 1)
    
    spi = summary.percent_complete / max(elapsed_ratio, 0.01)
    
    # Score based on SPI
    if spi >= 0.95:
        score = 100
    elif spi >= 0.85:
        score = 70
    elif spi >= 0.70:
        score = 40
    else:
        score = 20
    
    # Variance penalty: look at L1 milestones with variance data
    max_negative_variance = 0
    for task in project_data.milestones:
        if task.variance_days is not None and task.variance_days < max_negative_variance:
            max_negative_variance = task.variance_days
    
    # Cap score based on worst variance
    if max_negative_variance < -20:
        score = min(score, 30)
    elif max_negative_variance < -10:
        score = min(score, 50)
    
    detail = f"SPI={spi:.2f} ({"on track" if spi >= 0.95 else "behind"}). " \
             f"Project is {elapsed_ratio*100:.0f}% through timeline with {summary.percent_complete*100:.0f}% completion. " \
             f"Worst milestone variance: {max_negative_variance}d."
    
    return SignalResult(
        signal_name="Schedule Performance",
        score=score,
        weight=SIGNAL_WEIGHTS["schedule_performance"],
        weighted_score=score * SIGNAL_WEIGHTS["schedule_performance"],
        rag=_score_to_rag(score),
        detail=detail,
        raw_metrics={"spi": spi, "elapsed_ratio": elapsed_ratio, "worst_variance": max_negative_variance}
    )
```

### 4.10 `src/analysis/milestone_tracker.py`

**Function**: `analyze_milestones(project_data: ProjectData) -> SignalResult`

Logic:
1. Get all L1 milestones
2. For each, determine if it SHOULD be complete (planned_end < reference_date)
3. For each, determine if it's CURRENTLY ACTIVE (planned_start < reference_date < planned_end)
4. Score each milestone per the formula in Section 3
5. Average all milestone scores
6. Generate detail string listing each milestone and its health

**Expected Results** (pre-calculated for validation):

*S2P Project* (reference date: July 2):
- Contract Sign Off: Completed, planned_end Dec 5 → should be complete → ✅ 100
- Project Initiation & Data Gathering: Completed, planned_end Feb 27 → ✅ 100
- Config Doc Workshop: Completed, planned_end Mar 20 → ✅ 100
- Config & Build: In Progress 98%, planned_end May 19 → should be complete, >90% → 70
- UAT: Completed → ✅ 100
- TTT: Completed → ✅ 100
- Production & Cutover: In Progress 97%, planned_end Jun 12 → should be complete, >90% → 70
- Go-Live: Completed → ✅ 100
- Hypercare: In Progress **6%**, planned_end Jul 14 → ACTIVE, expected ~53%, actual 6% → 25
- Phase 2 P2P: In Progress 21%, planned_end Dec 7 → ACTIVE, expected ~35%, actual 21% → 25 (21/35 = 0.6, < 0.7)
- P2P Config Doc: In Progress 25%, planned_end Jul 13 → ACTIVE, expected ~100%, actual 25% → 25
- P2P Config & Build: Not Started, planned_start Jul 13 → future, skip
- P2P UAT, Cutover: Not Started, future → skip

Average of scored milestones ≈ (100+100+100+70+100+100+70+100+25+25+25) / 11 ≈ 74 → **GREEN/AMBER border**

*Project Plan B* (reference date: July 2):
- Multiple completed milestones → 100 each
- Training Phase I: In Progress 77%, planned_end May 28 → should be complete, <90% → 30
- Hypercare Phase I: In Progress 25%, planned_end Jul 06 → ACTIVE, expected ~85%, actual 25% → 25
- Config Validation (Phase II): In Progress 26%, planned_end Jul 22 → ACTIVE, expected ~39%, actual 26% → 60 (26/39 ≈ 0.67, < 0.7)
- eProc/eInvoice/Merlin: In Progress 21%, planned_end Aug 04 → ACTIVE
- Supplier Info Mgmt (Phase II): In Progress 12%, planned_end Aug 11 → ACTIVE

### 4.11 `src/analysis/blocker_detector.py`

**Function**: `analyze_blockers(project_data: ProjectData) -> SignalResult`

Logic:
1. Count On Hold tasks
2. Count "stalled" tasks: In Progress with % Complete < 10% AND planned_start was > 14 days before reference_date
3. Count At Risk tasks
4. Calculate blocker_ratio = total / active_tasks
5. Score per formula

**Expected Results**:
- S2P: 3 On Hold + ~5 stalled (Hypercare 6%, data tasks with 80-90% that are still stuck) → moderate
- Plan B: 0 On Hold, some stalled tasks → lower but still present

### 4.12 `src/analysis/resource_analyzer.py`

**Function**: `analyze_resources(project_data: ProjectData) -> SignalResult`

Logic:
1. Get active tasks (In Progress + Not Started)
2. Count how many have `assigned_to` not None/empty
3. coverage = assigned / total
4. Score per formula

**Expected Results**:
- S2P: 333/493 missing assignees, active tasks ~219, if 67.5% overall missing → coverage ≈ 32.5% → score ≈ 15 (RED)
- Plan B: 136/383 missing, active tasks ~234, missing rate 35.4% → coverage ≈ 64.6% → score ≈ 40 (AMBER-RED)

### 4.13 `src/analysis/trend_analyzer.py`

**Function**: `analyze_trends(current: RAGResult, historical: list[RAGResult]) -> TrendAnalysis`

This module compares RAG results across weeks:

```python
@dataclass
class TrendAnalysis:
    overall_direction: str          # "IMPROVING", "STABLE", "DECLINING"
    score_delta: float              # Change from last week
    signal_trends: dict[str, str]   # Per-signal trend direction
    emerging_risks: list[str]       # New risks this week
    insights: list[str]             # Cross-project observations
```

For the submission, we simulate 3 weeks of data by adjusting the reference date:
- Week 1 (June 18): reference_date = 2026-06-18
- Week 2 (June 25): reference_date = 2026-06-25
- Week 3 (July 2): reference_date = 2026-07-02

The task data stays the same (it's a snapshot), but the SPI and velocity calculations change because elapsed time changes, creating realistic trend data.

### 4.14 `src/agent/prompts.py` — EXACT PROMPT TEMPLATES

```python
WEEKLY_REPORT_SYSTEM_PROMPT = """You are a senior project management consultant generating a weekly project health report. 

You will receive:
1. A RAG status with composite score and individual signal scores
2. Raw project metrics and milestone data
3. Historical trend data (if available)

Your job is to write a clear, professional, plain-English report that:
- Explains WHY the project has its current RAG status (not just the color)
- Identifies the TOP 3 risks with specific data points
- Provides 3-5 actionable recommendations
- Uses executive-friendly language (a VP should understand it)
- References specific task names, dates, and numbers from the data
- Flags any data quality issues

Do NOT:
- Use vague language like "things are behind"
- Repeat the signal scores without context
- Make recommendations that aren't actionable
- Ignore the trend data if provided

Format your output as structured markdown with these sections:
## Executive Summary
## Signal Breakdown Analysis
## Top Risks
## Recommendations
## Trend Analysis (if historical data provided)
## Data Quality Notes
"""

WEEKLY_REPORT_USER_PROMPT = """Generate the weekly health report for:

Project: {project_name}
Project Manager: {project_manager}
Report Date: {reference_date}

=== RAG STATUS ===
Overall: {overall_rag} (Score: {composite_score}/100)
Data Confidence: {data_confidence:.0%}
{override_note}

=== SIGNAL SCORES ===
{signal_details}

=== MILESTONE STATUS ===
{milestone_summary}

=== KEY METRICS ===
- Total Tasks: {total_tasks}
- Completed: {completed} ({completed_pct:.0%})
- In Progress: {in_progress}
- Not Started: {not_started}
- On Hold: {on_hold}
- Missing Assignees: {missing_assignees} ({missing_assignee_pct:.0%})
- Project Timeline: {project_start} to {project_end} ({duration} days)
- Elapsed: {elapsed_days} days ({elapsed_pct:.0%})

=== RED/CRITICAL TASKS ===
{red_tasks}

=== COMMENTS/NOTES FROM PROJECT TEAM ===
{comments}

=== TREND DATA (vs previous week) ===
{trend_data}
"""

EXECUTIVE_PRESENTATION_PROMPT = """You are creating content for a 5-7 slide executive presentation on portfolio health. 
The audience is a VP-level client who needs to understand project health at a glance.

You will receive RAG reports for multiple projects across multiple weeks.

For each slide, provide:
1. Title (max 8 words)
2. Key Message (1 sentence subtitle)
3. Bullet points (max 5, each max 12 words)
4. Speaker notes (2-3 sentences of context)

The slides should:
1. Portfolio Overview Dashboard — both projects' status at a glance
2. Cross-Project Trend Analysis — what patterns emerge across projects
3. Critical Risk Assessment — top risks with impact and likelihood
4. Schedule Deep-Dive — where the delays are and why
5. Resource & Dependency Analysis — bottlenecks and gaps
6. Strategic Recommendations — prioritized action items with owners
7. 30-Day Outlook — what happens with and without intervention

Focus on TRENDS and INSIGHTS, not per-project summaries. A VP doesn't want to hear "Project A is red." They want to hear "Both projects show accelerating schedule slippage in post-UAT phases, suggesting a systemic gap in production readiness planning."

{reports_data}
"""
```

### 4.15 `src/agent/health_agent.py` — FULL SPECIFICATION

The agent orchestrates the full pipeline:

```python
class ProjectHealthAgent:
    """
    AI agent that reads project plans, determines RAG status,
    and provides plain-English reasoning.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = None  # Initialized lazily
        self.parser = ExcelParser()
        self.normalizer = DataNormalizer()
        self.rag_engine = RAGEngine()
        
    def analyze_project(self, filepath: Path, reference_date: date = None) -> tuple[ProjectData, RAGResult]:
        """Read a project file, normalize data, compute RAG."""
        # 1. Parse Excel
        raw_data = self.parser.parse(filepath)
        
        # 2. Normalize
        project_data = self.normalizer.normalize(raw_data, reference_date or self.settings.reference_date)
        
        # 3. Compute RAG
        rag_result = self.rag_engine.compute_rag(project_data)
        
        return project_data, rag_result
    
    def generate_weekly_report(self, project_data: ProjectData, rag_result: RAGResult, 
                                trend: TrendAnalysis = None) -> str:
        """Use LLM to generate plain-English weekly report."""
        # Build the prompt with all context
        prompt = self._build_report_prompt(project_data, rag_result, trend)
        
        # Call LLM
        if self.settings.openai_api_key:
            response = self._call_llm(WEEKLY_REPORT_SYSTEM_PROMPT, prompt)
        else:
            # Fallback: generate report WITHOUT LLM using templates
            response = self._generate_template_report(project_data, rag_result, trend)
        
        return response
    
    def generate_monthly_presentation(self, all_reports: list[dict]) -> Path:
        """Generate executive PPTX deck from accumulated reports."""
        # 1. Get LLM content for slides
        # 2. Generate charts with matplotlib
        # 3. Build PPTX with python-pptx
        pass
    
    def run_full_pipeline(self, data_dir: Path, output_dir: Path):
        """Complete pipeline: analyze all projects, generate reports + deck."""
        # 1. Find all .xlsx files in data_dir
        # 2. For each file, for each simulated week (3 weeks):
        #    a. analyze_project(file, reference_date=week_date)
        #    b. compute trends (if previous week exists)
        #    c. generate_weekly_report()
        #    d. save to outputs/weekly_reports/{date}/
        # 3. Generate monthly presentation from all reports
        # 4. Save to outputs/monthly_presentation/
        pass
```

**CRITICAL DESIGN DECISION — LLM Fallback**:
The agent MUST work even WITHOUT an OpenAI API key. If no key is provided:
- All deterministic analysis (RAG scoring, signal computation, trends) works normally
- Weekly reports are generated using a structured template (fill-in-the-blank) instead of LLM-generated prose
- The presentation content uses pre-written templates with computed data inserted

This ensures evaluators can `git clone && pip install && python run` WITHOUT needing an API key.

The LLM enhances the narrative quality but is NOT required for core functionality.

### 4.16 `src/reporting/weekly_report.py` — EXACT OUTPUT FORMAT

The generated markdown report for each project each week must follow this EXACT structure:

```markdown
# 📊 Weekly Project Health Report

**Project**: [Project Name]  
**Project Manager**: [Name]  
**Report Date**: [YYYY-MM-DD]  
**Report Generated By**: Project Health Reporting Agent v1.0

---

## Overall Status: [🔴 RED | 🟡 AMBER | 🟢 GREEN]
**Composite Score**: [XX]/100 | **Data Confidence**: [XX]%

---

## Executive Summary

[2-4 sentences of plain English explaining the overall health. Generated by LLM or template.]

Example for S2P: "The Titan S2P Implementation is at significant risk despite being 71% complete.
Phase 1 S2C is nearing completion at 92%, but Phase 2 P2P is severely behind at 21% completion 
with a -81 day variance against baseline. The Hypercare phase is critically stalled at 6% completion,
and 67.5% of tasks lack assigned owners, creating substantial execution risk."

---

## Signal Breakdown

| Signal | Score | Status | Weight | Detail |
|--------|-------|--------|--------|--------|
| Schedule Performance | [XX]/100 | [🔴/🟡/🟢] | 25% | [one-line detail] |
| Milestone Health | [XX]/100 | [🔴/🟡/🟢] | 20% | [one-line detail] |
| Task Velocity | [XX]/100 | [🔴/🟡/🟢] | 15% | [one-line detail] |
| Blocker Density | [XX]/100 | [🔴/🟡/🟢] | 15% | [one-line detail] |
| Resource Coverage | [XX]/100 | [🔴/🟡/🟢] | 10% | [one-line detail] |
| Dependency Risk | [XX]/100 | [🔴/🟡/🟢] | 15% | [one-line detail] |

---

## Milestone Status

| Phase | Status | Planned End | % Complete | Health | Variance |
|-------|--------|-------------|------------|--------|----------|
| [Each L1 milestone] | ... | ... | ... | ... | ... |

---

## 🚨 Top Risks

1. **[Risk Title]**: [Specific description with data points — dates, task names, variance numbers]
2. **[Risk Title]**: [...]
3. **[Risk Title]**: [...]

---

## ✅ Recommendations

1. **[Action]**: [Specific, actionable recommendation with suggested owner/timeline]
2. **[Action]**: [...]
3. **[Action]**: [...]

---

## 📈 Trend Analysis

| Metric | This Week | Last Week | Change | Direction |
|--------|-----------|-----------|--------|-----------|
| Composite Score | XX | XX | +/-X | ↑↓→ |
| Schedule Performance | XX | XX | +/-X | ↑↓→ |
| [Each signal] | ... | ... | ... | ... |

**Overall Trajectory**: [IMPROVING / STABLE / DECLINING]

---

## ⚠️ Data Quality Notes

- Fields with missing data: [count]
- Tasks without assignees: [count] ([%])
- Unparseable formula fields: [count]
- **Overall Data Confidence**: [XX]%

---

*Report generated automatically by Project Health Reporting Agent*
```

### 4.17 `src/reporting/presentation.py` — EXACT SLIDE SPECIFICATIONS

Use `python-pptx` to generate a professional 7-slide PPTX.

**Slide Dimensions**: Widescreen 16:9 (13.333" × 7.5")

**Color Scheme**:
```python
COLORS = {
    "primary_dark": RGBColor(0x1B, 0x2A, 0x4A),      # Dark navy
    "primary_medium": RGBColor(0x2D, 0x4A, 0x7A),     # Medium blue
    "accent": RGBColor(0x00, 0x96, 0xD6),             # Bright blue
    "red": RGBColor(0xE8, 0x3E, 0x3E),                # Status red
    "amber": RGBColor(0xF5, 0xA6, 0x23),              # Status amber
    "green": RGBColor(0x2E, 0xCC, 0x71),              # Status green
    "white": RGBColor(0xFF, 0xFF, 0xFF),
    "light_gray": RGBColor(0xF0, 0xF0, 0xF0),
    "dark_text": RGBColor(0x33, 0x33, 0x33),
}
```

**Font**: Calibri (built into PowerPoint)

**Slide-by-Slide Specification**:

#### Slide 1: Portfolio Health Overview
- **Title**: "Portfolio Health Overview — July 2026"
- **Layout**: 
  - Top: Title bar (dark navy background, white text)
  - Left half: Project A status card (project name, RAG badge, composite score, key metrics)
  - Right half: Project B status card (same format)
  - Bottom: Key portfolio metrics bar (total tasks, completion rate, critical risks count)
- **Data to include**:
  - S2P: 🟡/🔴 AMBER/RED, Score: XX/100, 71% complete, PM: Aftab Hashambhai
  - Plan B: 🔴 RED, Score: XX/100, 44% complete, PM: Rajat Bothra
  - Portfolio: X total tasks, Y active risks, Z blocked items

#### Slide 2: Cross-Project Trend Analysis
- **Title**: "Health Trends — 3-Week Rolling View"
- **Content**: 
  - Embed a matplotlib line chart (saved as PNG, inserted into slide)
  - Chart: X-axis = 3 weeks, Y-axis = composite score (0-100)
  - Two lines: S2P Project (blue) and Project Plan B (red)
  - Horizontal bands for Green (≥70), Amber (40-70), Red (<40) zones
  - Below chart: 3-4 bullet points identifying patterns
- **Chart generation code** (in `src/reporting/charts.py`):
  ```python
  def create_trend_chart(s2p_scores: list[float], planb_scores: list[float], 
                          weeks: list[str], output_path: Path):
      fig, ax = plt.subplots(figsize=(10, 5))
      ax.axhspan(70, 100, alpha=0.1, color='green')   # Green zone
      ax.axhspan(40, 70, alpha=0.1, color='orange')    # Amber zone
      ax.axhspan(0, 40, alpha=0.1, color='red')        # Red zone
      ax.plot(weeks, s2p_scores, 'b-o', label='S2P Project (Titan)', linewidth=2)
      ax.plot(weeks, planb_scores, 'r-s', label='Project Plan B (UniSan)', linewidth=2)
      ax.set_ylabel('Composite Health Score')
      ax.set_xlabel('Week')
      ax.set_ylim(0, 100)
      ax.legend()
      ax.grid(True, alpha=0.3)
      fig.tight_layout()
      fig.savefig(output_path, dpi=150, bbox_inches='tight')
  ```

#### Slide 3: Critical Risk Matrix
- **Title**: "Risk Assessment Matrix"
- **Content**:
  - 2×2 matrix (Impact: High/Med on Y-axis, Likelihood: High/Med on X-axis)
  - Place top 5-6 risks as colored circles in the matrix
  - Each risk labeled with short name
  - Risk list below matrix with details
- **Risks to include** (derived from analysis):
  1. Phase 2 P2P -81d behind (S2P) — High Impact, High Likelihood → RED quadrant
  2. Hypercare 6% complete with -30d variance (S2P) — High/High → RED
  3. Training Phase I 17d slip (Plan B) — Med/High → AMBER
  4. 67.5% tasks unassigned (S2P) — High/Med → AMBER-RED
  5. Cascading delays from Phase 1 to Phase 2 (S2P) — High/High → RED
  6. Config Documentation bottleneck (Plan B) — Med/Med → AMBER

#### Slide 4: Schedule Performance Deep-Dive
- **Title**: "Schedule Analysis — Where We're Falling Behind"
- **Content**:
  - Embed a horizontal bar chart showing each L1 milestone's planned vs actual progress
  - Color bars: green = on/ahead of schedule, red = behind
  - Highlight the worst offenders with callout boxes
- **Chart**: Grouped horizontal bars for key milestones of both projects

#### Slide 5: Resource & Dependency Analysis
- **Title**: "Resource Gaps & Dependency Risks"
- **Content**:
  - Left: Donut chart showing assigned vs unassigned tasks per project
  - Right: Key dependency bottlenecks (text + icons)
  - Bottom: "3 On Hold items blocking S2P progress: D&B credentials, Notification template, D&B App"

#### Slide 6: Strategic Recommendations
- **Title**: "Recommended Actions — Prioritized"
- **Content**:
  - Table with columns: Priority | Action | Owner | Timeline | Impact
  - 5-6 rows of specific, actionable recommendations
  - Use color coding for priority (🔴 Immediate, 🟡 This Week, 🟢 This Month)
- **Example Recommendations**:
  1. 🔴 "Assign dedicated resources to S2P Phase 2 P2P — currently 0 of 194 tasks have owners"
  2. 🔴 "Escalate Hypercare Phase I (6% complete, -30d variance) — risk of missed SLA"
  3. 🟡 "Resolve 3 On Hold blockers in S2P (D&B credentials, notification template)"
  4. 🟡 "Accelerate Training Phase I completion in Plan B (17d behind, blocking Hypercare)"
  5. 🟢 "Establish weekly cross-project sync to align Phase 2 timelines"

#### Slide 7: 30-Day Outlook
- **Title**: "30-Day Forecast — With & Without Intervention"
- **Content**:
  - Two columns: "Current Trajectory" vs "With Recommended Actions"
  - Current: Project specific predictions based on velocity
  - With Actions: Expected improvement
  - Bottom: "Key Decision Point: By July 15, leadership must decide on Phase 2 P2P resource allocation"

### 4.18 `src/reporting/charts.py` — CHARTS TO GENERATE

Generate these charts as PNG files for embedding in reports and presentation:

1. **`trend_chart.png`**: Line chart of composite scores over 3 weeks (2 lines, RAG zone bands)
2. **`milestone_health_chart.png`**: Horizontal bar chart of milestone completion vs expected
3. **`signal_radar_chart.png`**: Radar/spider chart of 6 signal scores (one per project)
4. **`resource_donut.png`**: Donut chart of assigned vs unassigned tasks
5. **`risk_matrix.png`**: 2×2 scatter plot of risks by impact × likelihood

All charts must:
- Use the defined color scheme
- Have clear labels and legends
- Be saved at 150 DPI minimum
- Use `plt.style.use('seaborn-v0_8-whitegrid')` for clean aesthetic
- Have transparent backgrounds where useful for PPTX embedding

### 4.19 `src/scheduler/weekly_scheduler.py`

```python
"""
Weekly scheduler using APScheduler.
Watches the data directory for Excel files and runs analysis every Monday at 9 AM.
"""
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
from datetime import date

def weekly_job(data_dir: Path, output_dir: Path):
    """Job that runs weekly."""
    from src.agent.health_agent import ProjectHealthAgent
    from src.config import Settings
    
    agent = ProjectHealthAgent(Settings())
    agent.run_full_pipeline(data_dir, output_dir)
    print(f"✅ Weekly report generated for {date.today()}")

def start_scheduler(data_dir: Path = Path("data"), output_dir: Path = Path("outputs")):
    """Start the weekly scheduler."""
    scheduler = BlockingScheduler()
    scheduler.add_job(
        weekly_job,
        trigger=CronTrigger(day_of_week="mon", hour=9, minute=0),
        args=[data_dir, output_dir],
        name="weekly_health_report",
        id="weekly_health_report",
    )
    print("📅 Weekly scheduler started. Reports will be generated every Monday at 9:00 AM.")
    print("Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
```

### 4.20 `src/main.py` — CLI ENTRY POINT

```python
"""
CLI entry point for the Project Health Reporting Agent.

Usage:
    python -m src.main analyze                    # Analyze all projects
    python -m src.main report --week 2026-07-02   # Generate weekly reports
    python -m src.main presentation               # Generate executive deck
    python -m src.main schedule                    # Start weekly scheduler
    python -m src.main full-run                    # Complete pipeline
"""
import typer
from pathlib import Path
from datetime import date
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="🏥 Project Health Reporting Agent")
console = Console()

@app.command()
def analyze(data_dir: Path = Path("data")):
    """Analyze all project files and display RAG status."""
    # Import agent, find xlsx files, compute RAG for each, print rich table
    pass

@app.command()
def report(data_dir: Path = Path("data"), output_dir: Path = Path("outputs"),
           week: str = None):
    """Generate weekly health reports."""
    pass

@app.command()
def presentation(data_dir: Path = Path("data"), output_dir: Path = Path("outputs")):
    """Generate executive monthly presentation."""
    pass

@app.command()
def schedule(data_dir: Path = Path("data"), output_dir: Path = Path("outputs")):
    """Start weekly scheduled reporting."""
    pass

@app.command()
def full_run(data_dir: Path = Path("data"), output_dir: Path = Path("outputs")):
    """Run complete pipeline: analyze → reports (3 weeks) → presentation."""
    # 1. Print banner
    # 2. For each of 3 reference dates [2026-06-18, 2026-06-25, 2026-07-02]:
    #    a. For each xlsx file in data_dir:
    #       - analyze_project(file, ref_date)
    #       - generate_weekly_report()
    #       - save to outputs/weekly_reports/{ref_date}/
    # 3. Compute trends across weeks
    # 4. Generate monthly presentation
    # 5. Print summary table
    pass

if __name__ == "__main__":
    app()
```

### 4.21 `tests/test_rag_engine.py` — EXACT TEST CASES

```python
"""
Unit tests for the RAG scoring engine.
Tests use manually constructed project data to verify scoring logic.
"""
import pytest
from src.analysis.rag_engine import RAGEngine, compute_rag
from src.ingestion.normalizer import ProjectData, ProjectSummary, NormalizedTask
from src.config import RAGStatus, TaskStatus
from datetime import date

class TestSchedulePerformance:
    def test_on_track_project(self):
        """Project at 50% complete at 50% elapsed time → SPI = 1.0 → score 100"""
        # Build ProjectData with 50% complete, start Jan 1, end Dec 31, today Jul 1
        pass
    
    def test_behind_schedule(self):
        """Project at 30% complete at 70% elapsed → SPI = 0.43 → score 20"""
        pass
    
    def test_variance_penalty(self):
        """Project with SPI=1.0 but -25d variance on milestone → score capped at 30"""
        pass

class TestMilestoneHealth:
    def test_all_milestones_complete(self):
        """All milestones completed → score 100"""
        pass
    
    def test_missed_milestone(self):
        """Milestone past due at 20% → score should be low"""
        pass

class TestCompositeScore:
    def test_green_project(self):
        """All signals healthy → GREEN"""
        pass
    
    def test_red_override(self):
        """Composite is 50 (AMBER) but schedule signal is 15 with weight 25% → override to RED"""
        pass
    
    def test_multi_signal_red_override(self):
        """3 signals below 40 → force RED regardless of composite"""
        pass

class TestDataConfidence:
    def test_low_confidence_warning(self):
        """Data quality < 50% → LOW CONFIDENCE appended"""
        pass
    
    def test_insufficient_data(self):
        """Data quality < 30% → INSUFFICIENT DATA status"""
        pass

class TestIntegration:
    def test_s2p_project_full(self):
        """Full RAG computation on actual S2P data → should be RED or AMBER"""
        pass
    
    def test_plan_b_full(self):
        """Full RAG computation on actual Plan B data → should be RED"""
        pass
```

---

## 5. PHASE 3: SAMPLE WEEKLY REPORT OUTPUTS

### 5.1 Strategy for 3 Weeks of Reports

The data files are snapshots as of July 2, 2026. To generate 3 weeks of historical reports:

**Week 1 (June 18, 2026)**: Set `reference_date = 2026-06-18`
- The same task data is used, but SPI changes because elapsed time is smaller
- Tasks that show as "Completed" with end dates after June 18 would still be "In Progress" in reality, but since we only have a snapshot, we use the data as-is and note this limitation
- This still shows meaningful variation because the velocity calculations change

**Week 2 (June 25, 2026)**: Set `reference_date = 2026-06-25`
- Intermediate state

**Week 3 (July 2, 2026)**: Set `reference_date = 2026-07-02`
- Current state matching the data's "Today's Date"

This gives us 6 reports total (2 projects × 3 weeks) that show meaningful trends.

### 5.2 Expected Approximate RAG Outcomes

| Week | S2P (Titan) | Plan B (UniSan) | Notes |
|---|---|---|---|
| June 18 | AMBER (~50-55) | AMBER (~45-55) | Earlier in timeline, less elapsed, velocity looks better |
| June 25 | AMBER-RED (~40-48) | RED (~35-42) | Plan B's training slip becomes visible |
| July 2 | RED (~30-38) | RED (~28-35) | Both projects show declining health |

### 5.3 File Naming Convention
```
outputs/weekly_reports/2026-06-18/s2p_project_report.md
outputs/weekly_reports/2026-06-18/project_plan_b_report.md
outputs/weekly_reports/2026-06-25/s2p_project_report.md
outputs/weekly_reports/2026-06-25/project_plan_b_report.md
outputs/weekly_reports/2026-07-02/s2p_project_report.md
outputs/weekly_reports/2026-07-02/project_plan_b_report.md
```

---

## 6. PHASE 4: EXECUTIVE MONTHLY PRESENTATION

Already fully specified in Section 4.17. Key reminders:

- File: `outputs/monthly_presentation/executive_deck_july_2026.pptx`
- 7 slides exactly
- Professional corporate design (navy + blue + white)
- Embedded matplotlib charts (PNG → PPTX)
- VP-ready language: trends, not summaries
- Every insight has a "so what" and "now what"
- Cross-project analysis: "Both projects show systemic gap in post-UAT readiness"

---

## 7. PHASE 5: README AND DOCUMENTATION

### 7.1 README.md — EXACT STRUCTURE

```markdown
# 🏥 Project Health Reporting Agent

An AI-powered system that automatically analyzes project plans, determines RAG 
(Red/Amber/Green) health status using a weighted multi-signal scoring framework, 
and generates executive-ready reports and presentations.

## 🎯 Key Features

- **Deterministic RAG Scoring**: 6-signal weighted composite algorithm (not pure LLM guessing)
- **LLM-Enhanced Reasoning**: GPT-4o provides plain-English explanations of the quantitative scores
- **Messy Data Handling**: Gracefully handles missing fields, #UNPARSEABLE formulas, inconsistent schemas
- **Multi-Schema Support**: Automatically detects and normalizes different Excel column layouts
- **Trend Analysis**: Week-over-week health tracking with trajectory prediction
- **Executive Presentations**: Auto-generated PPTX decks with embedded charts
- **Weekly Scheduling**: APScheduler-based automation for recurring reports
- **Works Without API Key**: Core analysis runs fully offline; LLM enhances narratives only

## 🏗️ Architecture

[Include ASCII diagram from rag_methodology.md]

### Design Decisions

1. **Deterministic RAG + LLM Reasoning**: The RAG score is computed mathematically with 
   clear, auditable thresholds. The LLM is used ONLY for generating human-readable narratives. 
   This ensures reproducibility, explainability, and trust — a VP can ask "why is this Red?" 
   and get a precise, data-backed answer.

2. **Weighted Multi-Signal Approach**: Rather than a single metric, we evaluate 6 independent 
   health dimensions. This prevents masking — a project can be on-schedule but have zero 
   resource coverage, and our system catches both.

3. **Schema Auto-Detection**: The two provided project files have different column layouts 
   (33 vs 37 columns). The parser detects the schema from headers and maps accordingly, 
   making the system extensible to new project file formats.

4. **Graceful Degradation**: Missing data reduces confidence scores rather than crashing. 
   Every report includes a Data Confidence metric so stakeholders know how much to trust 
   the analysis.

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- (Optional) OpenAI API key for enhanced narratives

### Installation & Run

```bash
# Clone the repository
git clone https://github.com/ashraf/zycus-project-health-agent.git
cd zycus-project-health-agent

# Option 1: One-command run
chmod +x run.sh && ./run.sh

# Option 2: Manual setup
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# (Optional) Set up OpenAI API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run full pipeline
python -m src.main full-run
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `python -m src.main analyze` | Analyze all projects and display RAG status |
| `python -m src.main report` | Generate weekly health reports |
| `python -m src.main presentation` | Generate executive PPTX deck |
| `python -m src.main schedule` | Start weekly automated scheduler |
| `python -m src.main full-run` | Run complete pipeline (recommended) |

## 📊 Sample Output

### Weekly Report Preview
[Screenshot or markdown snippet of a generated report]

### Executive Deck Preview  
[Screenshots of 2-3 key slides]

## 📁 Project Structure

[Tree diagram of the repository]

## 🧪 Testing

```bash
python -m pytest tests/ -v
```

## 📄 Deliverables

| Deliverable | Location |
|-------------|----------|
| RAG Methodology | `rag_methodology.md` |
| Working Agent | `src/` |
| Sample Weekly Reports | `outputs/weekly_reports/` |
| Executive Presentation | `outputs/monthly_presentation/executive_deck_july_2026.pptx` |
| This README | `README.md` |

## 🛠️ Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Language | Python 3.11 | Industry standard for AI/data engineering |
| LLM | OpenAI GPT-4o | Best reasoning quality for narrative generation |
| Data Processing | openpyxl + pandas | Robust Excel handling |
| Agent Framework | LangChain | Production-grade LLM orchestration |
| Presentations | python-pptx | Programmatic PowerPoint generation |
| Charts | matplotlib | Publication-quality visualizations |
| Scheduling | APScheduler | Production-grade Python scheduling |
| CLI | typer + rich | Beautiful command-line interface |
| Config | pydantic | Type-safe settings management |
```

---

## 8. VERIFICATION CHECKLIST

Before submitting, verify ALL of the following:

### 8.1 Code Quality
- [ ] `python -m src.main full-run` completes without errors
- [ ] `python -m src.main full-run` works WITHOUT an API key (template fallback)
- [ ] `python -m src.main full-run` works WITH an API key (LLM narratives)
- [ ] `python -m pytest tests/ -v` — all tests pass
- [ ] No hardcoded file paths (uses relative paths from config)
- [ ] Both Excel files are parsed correctly
- [ ] Agent handles gracefully: missing columns, #UNPARSEABLE values, empty cells, missing sheets

### 8.2 Outputs
- [ ] 6 weekly reports generated (2 projects × 3 weeks)
- [ ] Each report follows the exact template structure
- [ ] Reports contain specific task names, dates, and numbers (not generic text)
- [ ] Trend data shows week-over-week changes
- [ ] Executive PPTX has 5-7 slides
- [ ] PPTX includes embedded charts (not just text)
- [ ] PPTX uses professional corporate design
- [ ] PPTX contains cross-project insights (not per-project summaries)

### 8.3 Documentation
- [ ] `rag_methodology.md` is approximately 1 page
- [ ] `rag_methodology.md` includes all 6 signals with thresholds
- [ ] `README.md` includes Quick Start with ≤ 3 commands
- [ ] `README.md` explains design decisions
- [ ] `README.md` includes project structure tree
- [ ] `.env.example` provided
- [ ] `run.sh` works as one-command launcher

### 8.4 Differentiators Present
- [ ] Deterministic RAG scoring (not just LLM judgment)
- [ ] Data confidence scoring visible in reports
- [ ] Signal breakdown table in every report
- [ ] Trend analysis across 3 weeks
- [ ] Cross-project pattern identification in presentation
- [ ] Risk matrix with impact × likelihood
- [ ] Working scheduler (bonus feature)
- [ ] CLI with `rich` formatted output
- [ ] Graceful degradation without API key
- [ ] Unit tests for core logic

---

## 9. TIMELINE

**Start**: July 10, 2026, 2:45 AM IST
**Deadline**: July 11, 2026, EOD IST (~11:59 PM)
**Available Time**: ~45 hours

| Block | Task | Est. Hours | Priority |
|-------|------|-----------|----------|
| 1 | Setup repo structure, requirements, config | 1h | P0 |
| 2 | `ingestion/parser.py` + `normalizer.py` | 3h | P0 |
| 3 | `analysis/` — all 6 signal analyzers + `rag_engine.py` | 4h | P0 |
| 4 | `agent/health_agent.py` + `prompts.py` + template fallback | 3h | P0 |
| 5 | `reporting/weekly_report.py` — generate all 6 reports | 2h | P0 |
| 6 | `reporting/charts.py` — all 5 chart types | 2h | P0 |
| 7 | `reporting/presentation.py` — 7-slide PPTX | 3h | P0 |
| 8 | `rag_methodology.md` (1-page document) | 1h | P0 |
| 9 | `main.py` CLI + `run.sh` | 1h | P1 |
| 10 | `scheduler/weekly_scheduler.py` | 0.5h | P1 |
| 11 | `tests/` — unit tests | 1.5h | P1 |
| 12 | `README.md` — comprehensive documentation | 1h | P0 |
| 13 | End-to-end testing + bug fixes | 2h | P0 |
| 14 | Final review, polish, ZIP/GitHub prep | 1h | P0 |
| **Total** | | **~26h** | |

### Execution Order
1. Blocks 1-2 first (foundation — nothing works without the parser)
2. Block 3 (core algorithm — the differentiator)
3. Block 8 (RAG methodology doc — can write while algo is fresh)
4. Blocks 4-5 (agent + reports — the primary deliverable)
5. Blocks 6-7 (charts + presentation — the wow factor)
6. Block 9 (CLI — wraps everything nicely)
7. Blocks 10-11 (scheduler + tests — bonus points)
8. Block 12 (README — write after everything works)
9. Blocks 13-14 (testing + submission)

---

## 10. WHAT MAKES THIS TOP 0.1%

| Dimension | Typical Submission | Our Submission |
|---|---|---|
| RAG Calculation | "Ask GPT what the status is" | 6-signal weighted scoring with deterministic thresholds |
| Data Handling | Crashes on missing data | Data confidence scoring + graceful degradation |
| Schema Support | Hardcoded for one file | Auto-detection for multiple schemas |
| Reports | Raw LLM text dump | Structured reports with signal tables + trend analysis |
| Presentation | Copy-paste text to slides | Programmatic PPTX with embedded matplotlib charts |
| Cross-Project | Per-project summary | Portfolio-level trend analysis and pattern identification |
| Scheduling | "You could use cron" | Working APScheduler implementation |
| Documentation | "How to run: open notebook" | Professional README + design rationale + RAG methodology PDF |
| Testing | None | Unit tests for core scoring logic |
| Offline Capability | Requires API key | Full template fallback — works without any API key |
| CLI | Jupyter notebook | Polished typer CLI with rich formatting |
| Extensibility | One-off script | Modular architecture — add new signals, new file formats easily |

---

*This plan leaves nothing to interpretation. Follow it step by step and the output will be exceptional. Let's build. 🚀*

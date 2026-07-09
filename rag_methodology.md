# RAG Status Methodology — Project Health Reporting Agent

This document defines the quantitative framework used by the Project Health Reporting Agent to evaluate and classify project status as Red, Amber, or Green (RAG). 

---

## 1. Quantitative Framework Overview
Rather than relying on qualitative impressions, this system calculates project health deterministically using a **Weighted Multi-Signal Composite Scoring Framework**. Six independent metrics (signals) are extracted from the project plan data, scored from 0 to 100, and combined using fixed weights to yield a composite score. The overall RAG status is determined by this composite score, subject to critical override rules.

---

## 2. Signal Definitions

| Signal | Weight | Focus Area | Calculation Logic |
| :--- | :--- | :--- | :--- |
| **Schedule Performance** | 25% | Plan vs. Actual Timeline | Compares actual/forecasted end dates with the baseline. Calculates Schedule Performance Index ($SPI = \frac{\% \text{ Complete}}{\text{Elapsed Time Ratio}}$). Penalty caps apply for variances $> 10$ days. |
| **Milestone Health** | 20% | Critical Checkpoint Status | Evaluates all active or past L1 milestones. Scored by completion status vs. expected progress relative to reporting date. |
| **Task Velocity** | 15% | Completion Pace | Measures work output rate ($Velocity Ratio = \frac{\% \text{ Complete}}{\text{Elapsed Timeline Ratio}}$) to project if the project will close on schedule. |
| **Blocker Density** | 15% | Blockages and Stalls | Ratio of "On Hold", "At Risk", and stalled active tasks ($<10\%$ complete past planned start) to total active tasks. |
| **Resource Coverage** | 10% | Ownership and Staffing | The percentage of active (in-progress/not started) tasks that have an owner assigned in the "Assigned To" column. |
| **Dependency Risk** | 15% | Critical Path Health | Evaluates the percentage of critical path tasks showing delays and the count of active tasks with low float ($\le 3$ days). |

---

## 3. Thresholds & RAG Mapping

### Composite Scoring Thresholds
- 🟢 **GREEN**: Composite Score $\ge 70$ (Project is on track; schedule and resource risks are minor and manageable).
- 🟡 **AMBER**: $40 \le$ Composite Score $< 70$ (Project is experiencing slippage or resource shortages; active monitoring required).
- 🔴 **RED**: Composite Score $< 40$ (Project is in distress; key deliverables missed, or critical paths blocked).

### Critical Override Rules
To prevent critical issues from being masked by high scores in other areas, the following overrides are applied after composite scoring:
1. **Critical Signal Failure**: If any signal with a weight $\ge 20\%$ (Schedule or Milestone) scores $\le 20$, the overall status is forced to **RED**.
2. **Medium Signal Failure**: If any signal with a weight $\ge 15\%$ (Velocity, Blocker, or Dependency) scores $\le 10$, the overall status is forced to **RED**.
3. **Multi-Signal Distress**: If $\ge 3$ signals score $< 40$, status is forced to **RED**. If $\ge 2$ signals score $< 40$, status is forced to **AMBER** (minimum).

---

## 4. Assumptions & Edge Cases
1. **Reporting Reference Date**: Analysis is evaluated relative to the `Today's Date` value from the summary sheet (defaulting to July 2, 2026, for simulated project files).
2. **Missing Dates fallback**: When baseline dates are missing, planned dates are used as baselines. For `Project Plan B.xlsx`, `Baseline Start2/Finish2` are preferred.
3. **Data Completeness & Confidence**: A data quality score ($DQ$) is computed per task (non-null expected fields / total fields).
    - If $DQ < 50\%$: Overall status is marked **LOW CONFIDENCE**.
    - If $DQ < 30\%$: Overall status becomes **INSUFFICIENT DATA** (uncomputable).
4. **Tasks Exclusions**: Tasks marked "Not Applicable" or containing status "Not Applicable" are excluded from all calculations.
5. **In Progress Imputation**: Active tasks in progress with missing percent complete are imputed as $50\%$ complete.
6. **Budget Burn**: Budget and financial metrics (e.g. planned vs. actual cost) were not present in the provided Excel datasets. Therefore, budget burn is excluded from the quantitative RAG calculation. The system is designed to integrate cost-variance metrics (e.g., Cost Performance Index) as a 7th signal once financial tracking is added to the sheets.
7. **Stakeholder Sentiment**: Stakeholder and team sentiment is captured qualitatively from the text comments in the 'Comments' sheet (present in the S2P Titan file) and forwarded to the LLM agent's context window. It is not scored quantitatively due to the lack of a structured sentiment rating scale in the input files.

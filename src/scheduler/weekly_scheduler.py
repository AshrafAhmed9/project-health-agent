from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
from datetime import date


def weekly_job(data_dir: Path, output_dir: Path):
    """Analyze every project plan and save this week's health reports."""
    from src.agent.health_agent import ProjectHealthAgent
    from src.reporting.weekly_report import save_weekly_report

    ref_date = date.today()
    print(f"⏰ Starting scheduled weekly health check run for {ref_date}...")

    agent = ProjectHealthAgent()
    files = [f for f in data_dir.glob("*.xlsx") if not f.name.startswith("~$")]
    if not files:
        print(f"⚠️ No Excel project plans found in {data_dir}. Nothing to report.")
        return

    for f in files:
        try:
            proj_data, rag_res = agent.analyze_project(f, ref_date)
            report = agent.generate_weekly_report(proj_data, rag_res, trend=None)
            project_key = "s2p_project" if "s2p" in f.name.lower() else "project_plan_b"
            save_weekly_report(report, output_dir, str(ref_date), project_key)
            print(
                f"✓ Weekly report generated for {proj_data.summary.project_name} "
                f"({rag_res.overall_rag.value}, {rag_res.composite_score:.1f}/100)"
            )
        except Exception as e:
            print(f"⚠️ Failed to process {f.name}: {e}")


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
    print(
        "📅 Weekly scheduler started. Reports will be generated every Monday at 9:00 AM."
    )
    print("Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
        print("Scheduler stopped.")

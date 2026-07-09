from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from pathlib import Path
from datetime import date
from src.config import settings

def weekly_job(data_dir: Path, output_dir: Path):
    """Job that runs weekly."""
    from src.agent.health_agent import ProjectHealthAgent
    # Initialize agent and trigger run
    print(f"⏰ Starting scheduled weekly health check run for {date.today()}...")
    
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
        print("Scheduler stopped.")

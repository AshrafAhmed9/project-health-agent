import typer
from pathlib import Path
from datetime import date, datetime
from typing import Optional
from rich.console import Console
from rich.table import Table

from src.config import settings, RAGStatus, TaskStatus
from src.analysis.trend_analyzer import analyze_weekly_trends
from src.agent.health_agent import ProjectHealthAgent
from src.reporting.weekly_report import save_weekly_report
from src.reporting.charts import generate_trend_chart, generate_resource_donut
from src.reporting.presentation import PPTXGenerator
from src.scheduler.weekly_scheduler import start_scheduler

app = typer.Typer(help="🏥 Project Health Reporting Agent CLI")
console = Console()

@app.command()
def analyze(
    data_dir: Path = typer.Option(settings.data_dir, help="Directory containing project Excel files"),
    ref_date_str: str = typer.Option("2026-07-02", help="Reference date for analysis (YYYY-MM-DD)")
):
    """
    Perform a quick quantitative analysis of project health and print a status table.
    """
    ref_date = datetime.strptime(ref_date_str, "%Y-%m-%d").date()
    agent = ProjectHealthAgent()
    
    files = list(data_dir.glob("*.xlsx"))
    files = [f for f in files if f.name not in ("~$S2P Project.xlsx", "~$Project Plan B.xlsx")]
    
    if not files:
        console.print(f"[red]❌ No Excel files found in {data_dir}[/red]")
        raise typer.Exit(1)
        
    table = Table(title=f"Project Health Analysis Dashboard (Reference Date: {ref_date})")
    table.add_column("Project File", style="cyan")
    table.add_column("Project Name", style="white")
    table.add_column("Overall RAG", style="bold")
    table.add_column("Score", style="magenta")
    table.add_column("Completed", style="green")
    table.add_column("Active", style="yellow")
    table.add_column("Confidence", style="blue")
    
    for f in files:
        try:
            proj_data, rag_res = agent.analyze_project(f, ref_date)
            
            # Map status to color string
            rag_val = rag_res.overall_rag.value
            if rag_res.overall_rag == RAGStatus.GREEN:
                rag_styled = f"[green]{rag_val}[/green]"
            elif rag_res.overall_rag == RAGStatus.AMBER:
                rag_styled = f"[yellow]{rag_val}[/yellow]"
            else:
                rag_styled = f"[red]{rag_val}[/red]"
                
            active_count = proj_data.summary.in_progress_count + proj_data.summary.not_started_count + proj_data.summary.on_hold_count
            
            table.add_row(
                f.name,
                proj_data.summary.project_name,
                rag_styled,
                f"{rag_res.composite_score:.1f}/100",
                f"{proj_data.summary.completed_count} ({proj_data.summary.percent_complete*100:.0f}%)",
                str(active_count),
                f"{rag_res.data_confidence*100:.0f}%"
            )
        except Exception as e:
            console.print(f"[red]⚠️ Failed to parse {f.name}: {e}[/red]")
            
    console.print(table)

@app.command()
def report(
    data_dir: Path = typer.Option(settings.data_dir, help="Directory containing project Excel files"),
    output_dir: Path = typer.Option(settings.output_dir, help="Output directory"),
    ref_date_str: str = typer.Option("2026-07-02", help="Reference date for analysis (YYYY-MM-DD)")
):
    """
    Generate and save weekly health reports.
    """
    ref_date = datetime.strptime(ref_date_str, "%Y-%m-%d").date()
    agent = ProjectHealthAgent()
    
    files = list(data_dir.glob("*.xlsx"))
    files = [f for f in files if f.name not in ("~$S2P Project.xlsx", "~$Project Plan B.xlsx")]
    
    if not files:
        console.print(f"[red]❌ No Excel files found in {data_dir}[/red]")
        raise typer.Exit(1)
        
    for f in files:
        try:
            proj_data, rag_res = agent.analyze_project(f, ref_date)
            # Fetch report content (offline or online)
            report_content = agent.generate_weekly_report(proj_data, rag_res, trend=None)
            
            project_key = "s2p_project" if "s2p" in f.name.lower() else "project_plan_b"
            save_weekly_report(report_content, output_dir, ref_date_str, project_key)
            console.print(f"[green]✓ Generated report for {proj_data.summary.project_name} for date {ref_date_str}[/green]")
        except Exception as e:
            console.print(f"[red]⚠️ Failed to generate report for {f.name}: {e}[/red]")

@app.command()
def schedule_task(
    data_dir: Path = typer.Option(settings.data_dir, help="Data directory"),
    output_dir: Path = typer.Option(settings.output_dir, help="Output directory")
):
    """
    Start the background scheduler to run analysis weekly.
    """
    start_scheduler(data_dir, output_dir)

@app.command()
def full_run(
    data_dir: Path = typer.Option(settings.data_dir, help="Data directory"),
    output_dir: Path = typer.Option(settings.output_dir, help="Output directory")
):
    """
    Run complete workflow: analyses 3 simulated weeks, computes trends, draws charts, and generates executive PPTX deck.
    """
    console.print("[bold navy]🏥 Running Zycus Project Health Reporting Pipeline...[/bold navy]")
    
    simulated_weeks = ["2026-06-18", "2026-06-25", "2026-07-02"]
    agent = ProjectHealthAgent()
    
    # 1. Gather files
    files = list(data_dir.glob("*.xlsx"))
    files = [f for f in files if f.name not in ("~$S2P Project.xlsx", "~$Project Plan B.xlsx")]
    
    if not files:
        console.print("[red]❌ No Excel files found in data directory[/red]")
        raise typer.Exit(1)
        
    # Maps to track scores over weeks for line charts
    historical_results = {"s2p": [], "planb": []}
    project_data_map = {}
    reports_text_accumulator = ""
    
    # 2. Run analysis for each week
    for week_str in simulated_weeks:
        week_date = datetime.strptime(week_str, "%Y-%m-%d").date()
        console.print(f"\n[bold]📅 Analyzing Week: {week_str}[/bold]")
        
        for f in files:
            proj_key = "s2p" if "s2p" in f.name.lower() else "planb"
            try:
                proj_data, rag_res = agent.analyze_project(f, week_date)
                
                # Retrieve historical reports to build trends
                history = historical_results[proj_key]
                trend = analyze_weekly_trends(rag_res, history)
                
                # Save to history (pre-pend so that history[0] is most recent)
                historical_results[proj_key].insert(0, rag_res)
                project_data_map[proj_key] = proj_data # Keep latest week data
                
                # Generate weekly report markdown
                report_content = agent.generate_weekly_report(proj_data, rag_res, trend)
                
                # Save file
                file_key = "s2p_project" if proj_key == "s2p" else "project_plan_b"
                save_weekly_report(report_content, output_dir, week_str, file_key)
                
                if week_str == "2026-07-02":
                    reports_text_accumulator += f"\n=== REPORT FOR PROJECT: {proj_data.summary.project_name} ===\n"
                    reports_text_accumulator += report_content + "\n"
                    
            except Exception as e:
                console.print(f"[red]⚠️ Failed processing {f.name} for week {week_str}: {e}[/red]")
                import traceback
                traceback.print_exc()

    # 3. Generate Charts using weekly historical data
    # Reverse lists to plot chronologically
    s2p_scores = [r.composite_score for r in reversed(historical_results["s2p"])]
    planb_scores = [r.composite_score for r in reversed(historical_results["planb"])]
    
    trend_chart_path = output_dir / "charts" / "trend_chart.png"
    generate_trend_chart(simulated_weeks, s2p_scores, planb_scores, trend_chart_path)
    
    # Generate Resource Chart
    s2p_latest = project_data_map.get("s2p")
    planb_latest = project_data_map.get("planb")
    
    if s2p_latest and planb_latest:
        s2p_active = [t for t in s2p_latest.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)]
        s2p_assigned = sum(1 for t in s2p_active if t.assigned_to)
        s2p_unassigned = len(s2p_active) - s2p_assigned
        
        planb_active = [t for t in planb_latest.tasks if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.ON_HOLD)]
        planb_assigned = sum(1 for t in planb_active if t.assigned_to)
        planb_unassigned = len(planb_active) - planb_assigned
        
        resource_chart_path = output_dir / "charts" / "resource_chart.png"
        generate_resource_donut(s2p_assigned, s2p_unassigned, planb_assigned, planb_unassigned, resource_chart_path)
    else:
        resource_chart_path = Path("None")
        
    # 4. Generate Monthly Executive PPTX Presentation
    console.print("\n[bold]🖥️ Constructing executive PPTX presentation slides...[/bold]")
    slide_content = agent.generate_presentation_content(reports_text_accumulator)
    
    pptx_path = output_dir / "monthly_presentation" / "executive_deck_july_2026.pptx"
    generator = PPTXGenerator()
    generator.build_deck(slide_content, pptx_path, trend_chart_path, resource_chart_path)
    
    console.print("\n[bold green]🎉 Pipeline completed successfully![/bold green]")
    console.print(f"📂 Output directory: {output_dir}")

if __name__ == "__main__":
    app()

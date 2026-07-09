import os
from pathlib import Path

def save_weekly_report(report_content: str, output_dir: Path, date_str: str, project_key: str) -> Path:
    """
    Saves a generated weekly report to the outputs/weekly_reports/{date}/ folder.
    """
    target_dir = output_dir / "weekly_reports" / date_str
    target_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"{project_key}_report.md"
    filepath = target_dir / filename
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"📄 Weekly report saved to {filepath}")
    return filepath

from pathlib import Path
from src.ingestion.parser import ExcelParser

DATA_DIR = Path(__file__).parent.parent / "data"


def test_excel_parser_exists():
    parser = ExcelParser()
    assert parser is not None


def test_s2p_parsing():
    parser = ExcelParser()
    filepath = DATA_DIR / "S2P Project.xlsx"
    parsed = parser.parse(filepath)
    assert parsed["schema_type"] == "s2p"
    assert len(parsed["summary"]) > 0
    assert len(parsed["tasks_raw"]) > 400  # S2P has ~493 task rows


def test_plan_b_parsing():
    parser = ExcelParser()
    filepath = DATA_DIR / "Project Plan B.xlsx"
    parsed = parser.parse(filepath)
    assert parsed["schema_type"] == "plan_b"
    assert len(parsed["summary"]) > 0
    assert len(parsed["tasks_raw"]) > 300  # Plan B has ~383 task rows


def test_s2p_summary_fields():
    """Verify critical summary fields are extracted for S2P."""
    parser = ExcelParser()
    filepath = DATA_DIR / "S2P Project.xlsx"
    parsed = parser.parse(filepath)
    summary = parsed["summary"]
    assert summary.get("Project Manager") == "Aftab Hashambhai"
    assert summary.get("% Complete") is not None
    assert summary.get("Schedule Health") is not None


def test_plan_b_summary_fields():
    """Verify critical summary fields are extracted for Plan B."""
    parser = ExcelParser()
    filepath = DATA_DIR / "Project Plan B.xlsx"
    parsed = parser.parse(filepath)
    summary = parsed["summary"]
    assert summary.get("Project Manager") == "Rajat Bothra"
    assert summary.get("% Complete") is not None


def test_s2p_comments_exist():
    """S2P has real comments in the Comments sheet."""
    parser = ExcelParser()
    filepath = DATA_DIR / "S2P Project.xlsx"
    parsed = parser.parse(filepath)
    assert len(parsed["comments"]) > 0


def test_plan_b_comments_empty():
    """Plan B Comments sheet is empty."""
    parser = ExcelParser()
    filepath = DATA_DIR / "Project Plan B.xlsx"
    parsed = parser.parse(filepath)
    # Plan B comments sheet has 1 row with None
    assert (
        all(not any(c.values()) for c in parsed["comments"])
        or len(parsed["comments"]) <= 1
    )

from pathlib import Path
from enum import Enum
from datetime import date
from pydantic import Field
from pydantic_settings import BaseSettings


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


SIGNAL_WEIGHTS = {
    "schedule_performance": 0.25,
    "milestone_health": 0.20,
    "task_velocity": 0.15,
    "blocker_density": 0.15,
    "resource_coverage": 0.10,
    "dependency_risk": 0.15,
}

RAG_GREEN_THRESHOLD = 70
RAG_AMBER_THRESHOLD = 40

RED_OVERRIDE_SINGLE_HEAVY = 20  # If signal with weight >= 20% scores <= this -> RED
RED_OVERRIDE_SINGLE_MEDIUM = 10  # If signal with weight >= 15% scores <= this -> RED
RED_OVERRIDE_MULTI_COUNT = 3  # If N signals score below 40 -> RED
AMBER_OVERRIDE_MULTI_COUNT = 2  # If N signals score below 40 -> AMBER

LOW_CONFIDENCE_THRESHOLD = 0.5
INSUFFICIENT_DATA_THRESHOLD = 0.3


class Settings(BaseSettings):
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", validation_alias="OPENAI_MODEL")
    openai_api_base: str = Field(
        default="https://api.openai.com/v1", validation_alias="OPENAI_API_BASE"
    )

    data_dir: Path = Path("data")
    output_dir: Path = Path("outputs")
    reference_date: date = date(2026, 7, 2)  # "Today" per the data files

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

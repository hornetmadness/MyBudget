from typing import Set
import os
from pathlib import Path
from pydantic_settings import BaseSettings


def get_version() -> str:
    """Read version from version.txt file"""
    version_file = Path(__file__).parent.parent / "version.txt"
    if version_file.exists():
        return version_file.read_text().strip()
    return "1.0.0"


class Settings(BaseSettings):
    APP_NAME: str = "MyBudget"
    APP_VERSION: str = get_version()
    APP_DESCRIPTION: str = "A simple personal finance management application."
    POSTGRESQL_HOSTNAME: str = "localhost"
    POSTGRESQL_USERNAME: str = "postgres"
    POSTGRESQL_PASSWORD: str = "postgres"
    POSTGRESQL_DATABASE: str = "my_budget"


settings = Settings()

API_URL = os.getenv("API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mybudget.db")

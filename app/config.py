from typing import Set
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MyBudget"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A simple personal finance management application."
    POSTGRESQL_HOSTNAME: str = "localhost"
    POSTGRESQL_USERNAME: str = "postgres"
    POSTGRESQL_PASSWORD: str = "postgres"
    POSTGRESQL_DATABASE: str = "my_budget"


settings = Settings()

API_URL = os.getenv("API_URL", "http://localhost:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mybudget.db")

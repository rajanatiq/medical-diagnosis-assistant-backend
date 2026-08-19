import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Medical Diagnosis & Triage Assistant API"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"

    # Security & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "medical-diagnosis-assistant-secure-jwt-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # SQL Server Database Configuration
    # Connects to localhost\SQLEXPRESS with Windows Authentication (trusted_connection=yes)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "mssql+pyodbc://localhost\\SQLEXPRESS/medical_diagnosis_assistant?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )

    # CORS Origins for frontend clients
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()

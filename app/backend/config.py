"""
MEDHA Backend — Configuration
Loads all settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")


class Settings:
    # Database
    DATABASE_URL: str = f"sqlite:///{ROOT_DIR / 'medha.db'}"

    # HuggingFace Classifier
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_MODEL_ID: str = os.getenv("HF_MODEL_ID", "")
    HF_API_URL: str = f"https://router.huggingface.co/hf-inference/models/{os.getenv('HF_MODEL_ID', '')}"

    # AI APIs (for future use — notes are assembled, not generated)
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # App
    CORS_ORIGINS: list = ["*"]
    EQUILIBRIUM_SECONDS: int = 45  # 2025-26 BD medical: 75min / 100 questions
    SECRET_KEY: str = os.getenv("SECRET_KEY", "medha-dev-secret-key-change-in-prod")

    # Question data
    QUESTIONS_FILE: Path = ROOT_DIR / "data" / "questions.jsonl"


settings = Settings()

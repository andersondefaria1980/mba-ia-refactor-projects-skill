import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    SECRET_KEY = os.environ["SECRET_KEY"]
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 5000))
    DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    TOKEN_TTL_SECONDS = int(os.environ.get("TOKEN_TTL_SECONDS", 3600))
    NOTIFICATIONS_ENABLED = os.environ.get("NOTIFICATIONS_ENABLED", "false").lower() == "true"
    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

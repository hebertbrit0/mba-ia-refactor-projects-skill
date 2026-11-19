import os
import secrets

from dotenv import load_dotenv

load_dotenv()


class Settings:
    def __init__(self):
        self.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
        self.database_uri = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
        self.debug = os.environ.get("FLASK_DEBUG", "0") == "1"
        self.host = os.environ.get("HOST", "127.0.0.1")
        self.port = int(os.environ.get("PORT", "5000"))
        self.smtp_host = os.environ.get("SMTP_HOST", "localhost")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ.get("SMTP_USER", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")


settings = Settings()

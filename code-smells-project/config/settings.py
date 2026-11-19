import os
import secrets


class Settings:
    def __init__(self):
        self.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
        self.debug = os.environ.get("FLASK_DEBUG", "0") == "1"
        self.db_path = os.environ.get("DB_PATH", "loja.db")
        self.host = os.environ.get("HOST", "127.0.0.1")
        self.port = int(os.environ.get("PORT", "5000"))
        self.app_version = "1.0.0"
        self.environment = os.environ.get("APP_ENV", "development")


settings = Settings()

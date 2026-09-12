import os

APP_NAME = "LifeHub API"
# Override para testes via env var antes de importar o app.
DATABASE_URL = os.getenv("LIFEHUB_DATABASE_URL", "sqlite:///./lifehub.db")
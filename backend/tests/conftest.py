from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# IMPORTANTE: definir o banco temporário ANTES de importar o app,
# para que app.db crie o engine apontando para o arquivo de teste.
_db_file = Path(tempfile.mkdtemp()) / "test.db"
os.environ["LIFEHUB_DATABASE_URL"] = f"sqlite:///{_db_file}"

from app.db import get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base  # noqa: E402

_engine = create_engine(
    f"sqlite:///{_db_file}", connect_args={"check_same_thread": False}
)
_TestingSessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=_engine)
    Base.metadata.create_all(bind=_engine)

    def override_get_db():
        db = _TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
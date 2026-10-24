import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "backend")
sys.path.insert(0, BACKEND)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import json  # noqa: E402
import tempfile  # noqa: E402

import pytest  # noqa: E402

from generate_sample_seats import build  # noqa: E402

# Тесты всегда работают на синтетической схеме и не требуют data/seats.json.
_tmp = tempfile.mkdtemp()
SEATS_PATH = os.path.join(_tmp, "seats.json")
with open(SEATS_PATH, "w", encoding="utf-8") as f:
    json.dump(build(), f)
os.environ["SEATS_FILE"] = SEATS_PATH
os.chdir(BACKEND)  # ImageLibrary использует путь assets/images относительно backend/


@pytest.fixture(scope="session")
def seats_loader():
    from utils.seats_loader import SeatsLoader
    return SeatsLoader().load()


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from main import app
    return TestClient(app)

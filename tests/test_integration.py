import os

from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql://hostel:hostelpass@localhost:5432/hostel",
)
os.environ.setdefault(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

from app.main import app  # noqa: E402


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["postgres"] is True
    assert data["redis"] is True


def test_students_endpoint():
    response = client.get("/students")

    assert response.status_code == 200

    data = response.json()

    assert "students" in data
    assert len(data["students"]) == 20


def test_rooms_endpoint():
    response = client.get("/rooms")

    assert response.status_code == 200

    data = response.json()

    assert "rooms" in data
    assert len(data["rooms"]) == 10

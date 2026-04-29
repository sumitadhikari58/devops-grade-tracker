import pytest

from app import app, students


@pytest.fixture
def client():
    app.config["TESTING"] = True
    students.clear()
    with app.test_client() as client:
        yield client


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data["status"] == "ok"


def test_index_loads(client):
    r = client.get("/")
    assert r.status_code == 200


def test_add_student(client):
    r = client.post(
        "/add",
        data={
            "name": "Sumit",
            "roll": "21CS001",
            "subject": "DevOps",
            "score": "88",
        },
    )
    assert r.status_code == 302
    assert len(students) == 1
    assert students[0]["grade"] == "B"


def test_add_invalid_score(client):
    r = client.post(
        "/add",
        data={
            "name": "Test",
            "roll": "21CS002",
            "subject": "DevOps",
            "score": "999",
        },
    )
    assert r.status_code == 302
    assert len(students) == 0


def test_delete_student(client):
    client.post(
        "/add",
        data={
            "name": "Sumit",
            "roll": "21CS001",
            "subject": "DevOps",
            "score": "88",
        },
    )
    sid = students[0]["id"]
    r = client.post(f"/delete/{sid}")
    assert r.status_code == 302
    assert len(students) == 0


def test_api_students(client):
    r = client.get("/api/students")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)

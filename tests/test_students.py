"""Regression tests for the course's existing Bruno HTTP endpoints."""
import pytest
from app import create_app, db


@pytest.fixture()
def client(tmp_path):
    uri = "sqlite:///" + (tmp_path / "students-test.db").as_posix()
    application = create_app(uri)
    application.config["TESTING"] = True
    with application.app_context():
        db.create_all()  # Test setup only; real installs use flask db upgrade.
    with application.test_client() as test_client:
        yield test_client


def test_crud(client):
    assert client.get("/api/v1/students").get_json() == []
    created = client.post("/api/v1/students", json={"name": "Aaron", "age": 25})
    assert created.status_code == 201
    student_id = created.get_json()["id"]
    assert client.get(f"/api/v1/students/{student_id}").status_code == 200
    updated = client.put(f"/api/v1/students/{student_id}", json={"age": 26})
    assert updated.status_code == 200
    assert updated.get_json()["age"] == 26
    assert client.delete(f"/api/v1/students/{student_id}").status_code == 200
    assert client.get(f"/api/v1/students/{student_id}").status_code == 404


def test_validation(client):
    assert client.post("/api/v1/students", json={"name": "Missing age"}).status_code == 400
    assert client.post("/api/v1/students", json={"name": "A", "age": True}).status_code == 400
    assert client.post("/api/v1/students", json={"name": "", "age": 20}).status_code == 400
    assert client.get("/api/v1/students/999").status_code == 404


def test_persistence_between_app_instances(tmp_path):
    uri = "sqlite:///" + (tmp_path / "persistent.db").as_posix()
    first = create_app(uri)
    with first.app_context():
        db.create_all()
    assert first.test_client().post("/api/v1/students", json={
        "name": "Aaron", "age": 25
    }).status_code == 201
    second = create_app(uri)
    response = second.test_client().get("/api/v1/students")
    assert response.status_code == 200
    assert response.get_json()[0]["name"] == "Aaron"

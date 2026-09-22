from fastapi.testclient import TestClient

from src.api.api import app


client = TestClient(app)


def test_root():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Apex Manufacturing AI"
    assert data["status"] == "running"
    assert data["version"] == "1.0.0"


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"


def test_chat_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": ""
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == ""

    assert "Please provide" in data["answer"]


def test_chat_whitespace_question():
    response = client.post(
        "/chat",
        json={
            "question": "   "
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == ""

    assert "Please provide" in data["answer"]


def test_chat_response_structure():
    response = client.post(
        "/chat",
        json={
            "question": "What is the overall production efficiency?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "question" in data
    assert "answer" in data

    assert data["question"] == (
        "What is the overall production efficiency?"
    )

    assert isinstance(data["answer"], str)
    assert len(data["answer"]) > 0
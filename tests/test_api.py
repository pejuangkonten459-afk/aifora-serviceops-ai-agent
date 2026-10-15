from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_root_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["project_code"] == "01.AIFORA.10.26"


def test_list_requests():
    with TestClient(app) as client:
        response = client.get("/requests")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_audit_logs():
    with TestClient(app) as client:
        response = client.get("/audit-logs")

    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_request_writes_audit_log():
    with TestClient(app) as client:
        create_response = client.post(
            "/requests",
            json={
                "title": "Pemeriksaan audit log",
                "description": "Perangkat perlu diperiksa untuk pengujian audit.",
            },
        )

        assert create_response.status_code == 201
        request_id = create_response.json()["id"]

        audit_response = client.get("/audit-logs")

    assert audit_response.status_code == 200

    matching_logs = [
        log
        for log in audit_response.json()
        if log["request_id"] == request_id
        and log["action"] == "request.created"
    ]

    assert len(matching_logs) == 1
    assert "category=" in matching_logs[0]["details"]
    assert "priority=" in matching_logs[0]["details"]

def test_create_request():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={
                "title": "Laptop rusak untuk pengujian",
                "description": "Laptop tidak berfungsi dan perlu diperiksa.",
            },
        )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["category"] == "maintenance"
    assert data["priority"] == "high"
    assert data["status"] == "received"


def test_create_request_validation():
    with TestClient(app) as client:
        response = client.post(
            "/requests",
            json={
                "title": "AB",
                "description": "Data pengujian",
            },
        )

    assert response.status_code == 422

def test_get_request_not_found():
    with TestClient(app) as client:
        response = client.get("/requests/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Request not found."


def test_create_request_rolls_back_when_audit_log_fails():
    from unittest.mock import MagicMock

    from app.main import get_db

    mock_db = MagicMock()
    mock_db.flush.return_value = None
    mock_db.commit.side_effect = RuntimeError(
        "Simulated database failure"
    )

    def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            response = client.post(
                "/requests",
                json={
                    "title": "Uji kegagalan audit",
                    "description": "Perangkat perlu diperiksa untuk uji rollback.",
                },
            )

        assert response.status_code == 500
        assert response.json()["detail"] == (
            "Failed to save request and audit log."
        )
        mock_db.rollback.assert_called_once()
    finally:
        app.dependency_overrides.pop(get_db, None)





def test_rag_answer_success(monkeypatch):
    def fake_build_answer(query: str, n_results: int = 2):
        return {
            "query": query,
            "answer": "Periksa kabel jaringan dan koneksi Wi-Fi.",
            "sources": ["SOP-001-gangguan-jaringan.md"],
            "method": "extractive_rag",
        }

    monkeypatch.setattr(
        "app.main.build_answer",
        fake_build_answer,
    )

    with TestClient(app) as client:
        response = client.post(
            "/rag/answer",
            json={
                "query": "Internet terputus",
                "n_results": 2,
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "Internet terputus"
    assert "Periksa kabel jaringan" in data["answer"]
    assert data["sources"] == ["SOP-001-gangguan-jaringan.md"]
    assert data["method"] == "extractive_rag"


def test_rag_answer_rejects_short_query():
    with TestClient(app) as client:
        response = client.post(
            "/rag/answer",
            json={
                "query": " a ",
                "n_results": 2,
            },
        )

    assert response.status_code == 422

def test_rag_answer_rejects_unrelated_question(monkeypatch):
    def fake_build_answer(query: str, n_results: int = 2):
        return {
            "query": query,
            "answer": (
                "Belum ditemukan informasi SOP yang cukup relevan "
                "untuk menjawab pertanyaan ini."
            ),
            "sources": [],
            "method": "extractive_rag",
        }

    monkeypatch.setattr(
        "app.main.build_answer",
        fake_build_answer,
    )

    with TestClient(app) as client:
        response = client.post(
            "/rag/answer",
            json={
                "query": "Bagaimana cara mengajukan cuti tahunan?",
                "n_results": 2,
            },
        )

    assert response.status_code == 200

    data = response.json()
    assert data["sources"] == []
    assert "Belum ditemukan" in data["answer"]
    assert data["method"] == "extractive_rag"

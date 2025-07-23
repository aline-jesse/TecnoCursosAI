import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_export_video():
    payload = {
        "scenes": [{"id": "1", "name": "Cena Teste", "duration": 5}],
        "quality": "1080p",
        "format": "mp4",
        "fps": 30
    }
    response = client.post("/api/export-video", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["videoUrl"].endswith(".mp4")
    assert "exportId" in data


def test_regenerate_narration():
    payload = {
        "text": "Olá, este é um teste de narração IA.",
        "sceneId": "1",
        "voice": "default"
    }
    response = client.post("/api/regenerate-narration", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["narrationUrl"].endswith(".mp3") 
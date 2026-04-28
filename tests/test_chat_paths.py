import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestChatPaths:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_graph_going_through_path_a(self, client):
        response = client.post("/chat", json={"prompt": "how are u? I just want to go fast, first choice!"})
        assert response.status_code == 200
        assert response.cookies.get("thread_id") is not None
        assert response.json() is not None

        path = response.json().get("path")
        assert path == "path_a"

    def test_graph_going_through_path_b(self, client):
        response = client.post("/chat", json={"prompt": "Im looking for altenratives..."})
        assert response.status_code == 200
        assert response.cookies.get("thread_id") is not None
        assert response.json() is not None

        path = response.json().get("path")
        assert path == "path_b"

    def test_graph_going_through_path_unknown(self, client):
        response = client.post("/chat", json={"prompt": "I want to order food."})
        assert response.status_code == 200
        assert response.cookies.get("thread_id") is not None
        assert response.json() is not None

        path = response.json().get("path")
        assert path == "unknown_path"

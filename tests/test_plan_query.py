import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestSimpleQuery:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_should_make_simple_query(self, client):
        response = client.post(f"/chat", json={"prompt": "Show me how many people bough milk last week"})

        assert response.status_code == 200
        assert response.json() is not None

        complexity = response.json().get("complexity")
        assert "simple" in complexity.lower()

    def test_should_make_a_complex_query(self, client):
        response = client.post(f"/chat", json={"prompt": "Find purchases that customers typically purchase after buying milk"})

        assert response.status_code == 200
        assert response.json() is not None

        complexity = response.json().get("complexity")
        assert "complex" in complexity.lower()
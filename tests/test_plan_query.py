import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestSimpleQuery:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_should_make_simple_query(self, client):
        response = client.post(f"/chat", json={"prompt": "Show me how many people bough Apple last year"})

        assert response.status_code == 200
        assert response.json() is not None

        complexity = response.json().get("complexity")
        assert "simple" in complexity.lower()

        total_steps = response.json().get("total_steps")
        assert total_steps == 1

    def test_should_make_a_complex_query(self, client):
        response = client.post(f"/chat", json={"prompt": "Find purchases that customers typically purchase after buying milk"})

        assert response.status_code == 200
        assert response.json() is not None

        complexity = response.json().get("complexity")
        assert "complex" in complexity.lower()

        total_steps = response.json().get("total_steps")
        assert total_steps > 1
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

        body = response.json()

        complexity = body.get("complexity")
        total_steps = body.get("total_steps")
        cyphers_results = body.get("cyphers_results")

        assert "simple" in complexity.lower()
        assert total_steps == 1
        assert len(cyphers_results) == 1

    def test_should_make_a_complex_query(self, client):
        response = client.post(f"/chat", json={"prompt": "Find purchases that customers typically purchase after buying milk"})

        assert response.status_code == 200
        assert response.json() is not None

        body = response.json()

        complexity = body.get("complexity")
        total_steps = body.get("total_steps")
        cyphers_results = body.get("cyphers_results")

        assert "complex" in complexity.lower()
        assert total_steps > 1
        assert len(cyphers_results) == total_steps
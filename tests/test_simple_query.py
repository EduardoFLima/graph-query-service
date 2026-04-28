import pytest
from fastapi.testclient import TestClient
from src.main import app


class TestSimpleQuery:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_a_simple_query(self, client):
        pass

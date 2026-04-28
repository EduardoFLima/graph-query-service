import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestChatPersistence:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_graph_should_remember_previous_iteration(self, client):
        pass

    def test_graph_should_keep_memory_when_thread_id_is_not_given(self, client):
        pass
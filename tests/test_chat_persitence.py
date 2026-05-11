from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.main import app


class TestChatPersistence:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_graph_should_remember_previous_iteration(self, client):
        thread_id = "test_graph_should_remember_previous_path" + str(datetime.now())
        # first call
        client.cookies.set("thread_id", thread_id)
        first_question = "list the products sold last week."
        response = client.post("/chat", json={"prompt": first_question})
        assert response.status_code == 200

        # the second call should remember the path
        response = client.post("/chat?show_history=true", json={"prompt": "What was my last question?"})
        assert response.status_code == 200
        assert response.json() is not None
        messages = response.json().get("messages")

        assert first_question in messages[0]

    def test_graph_should_keep_memory_when_thread_id_is_not_given(self, client):
        # first call
        first_question = "list the products sold last week."
        response = client.post("/chat", json={"prompt": first_question})
        assert response.status_code == 200

        # the second call should remember the path
        response = client.post("/chat?show_history=true", json={"prompt": "What was my last question?"})
        assert response.status_code == 200
        assert response.json() is not None
        messages = response.json().get("messages")

        assert first_question in messages[0]

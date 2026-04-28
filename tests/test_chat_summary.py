import uuid

import pytest
from httpx import Response
from starlette.testclient import TestClient

from src.main import app


def send_message_to_chat(client: TestClient, user_id, message: str) -> Response:
    response = client.post(f"/chat?user_id={user_id}&show_history=true", json={"prompt": message})

    assert response.status_code == 200
    assert response.json() is not None
    assert response.cookies is not None

    return response


class TestChatPersistence:

    @pytest.fixture()
    def client(self):
        return TestClient(app)

    def test_graph_should_make_a_summary_after_hitting_the_threshold(self, client):
        user_id = str(uuid.uuid4())

        response = send_message_to_chat(client, user_id, "how are u?")

        thread_id = response.cookies.get("thread_id")

        send_message_to_chat(client, user_id, "this is fun!")
        response = send_message_to_chat(client, user_id, "what are you capable of?")

        messages = response.json().get("messages")
        assert messages is not None
        assert len(messages) == 6

        send_message_to_chat(client, user_id, "ah ! thank you")
        response = send_message_to_chat(client, user_id, "You are very smart.")

        assert thread_id == response.cookies.get("thread_id")
        messages = response.json().get("messages")
        assert messages is not None
        assert len(messages) == 6

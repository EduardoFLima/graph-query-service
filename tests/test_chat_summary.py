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

        response = send_message_to_chat(client, user_id, "how are u? I just want to go fast, first choice!")

        path = response.json().get("path")
        assert path == "path_a"
        thread_id = response.cookies.get("thread_id")

        send_message_to_chat(client, user_id, "this is fun!")
        response = send_message_to_chat(client, user_id, "what path did I take previously?")

        messages = response.json().get("messages")
        assert messages is not None
        assert len(messages) == 6

        send_message_to_chat(client, user_id, "ah ! thank you")
        send_message_to_chat(client, user_id, "what if i take another path?")
        response = send_message_to_chat(client, user_id, "You are very smart. Take the path I did previously!")

        path = response.json().get("path")
        assert path == "path_a"
        assert thread_id == response.cookies.get("thread_id")
        messages = response.json().get("messages")
        assert messages is not None
        assert len(messages) == 6

    def test_graph_should_store_preferences_based_on_conversation_history_summary(self, client):
        user_id = str(uuid.uuid4())

        send_message_to_chat(client, user_id, "how are u? I just want to go fast, first choice!")
        send_message_to_chat(client, user_id, "take the path a!")
        response = send_message_to_chat(client, user_id, "take the path b!")

        # return another path based on the latest message even when the preferred path is other
        path = response.json().get("path")
        assert path == "path_b"
        preferred_path = response.json().get("preferred_path")
        assert preferred_path == "path_a"

        # in case they "tie", return the latest
        response = send_message_to_chat(client, user_id, "take the path b!")

        preferred_path = response.json().get("preferred_path")
        assert preferred_path == "path_b"

        # return the preferred one, when user asks for it
        send_message_to_chat(client, user_id, "take the path a!")
        response = send_message_to_chat(client, user_id, "take the path do I prefer")

        path = response.json().get("path")
        assert path == "path_a"


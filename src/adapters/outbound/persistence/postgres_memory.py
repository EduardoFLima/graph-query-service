from langgraph.checkpoint.postgres import PostgresSaver

from src.application.ports.outbound.memory_port import MemoryPort


class PostgresMemory(MemoryPort):

    def __init__(self, db_uri: str):
        self._db_uri = db_uri

        self._checkpointer_context_manager = None
        self._checkpointer = None

        self.start()

    def get_checkpointer(self):
        return self._checkpointer

    def start(self):
        self._checkpointer_context_manager = PostgresSaver.from_conn_string(self._db_uri)
        self._checkpointer = self._checkpointer_context_manager.__enter__()
        self._checkpointer.setup()

    def stop(self):
        if self._checkpointer_context_manager:
            self._checkpointer_context_manager.__exit__(None, None, None)

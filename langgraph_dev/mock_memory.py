from src.application.ports.outbound.memory_port import MemoryPort


class MockMemory(MemoryPort):

    def __init__(self):
        self._checkpointer = None
        self._store = None

        self.start()

    def get_checkpointer(self):
        return self._checkpointer

    def get_store(self):
        return self._store

    def start(self):
        pass

    def stop(self):
        pass

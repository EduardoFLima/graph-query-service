from langgraph.store.postgres import PostgresStore


class PostgresStoreRepository(PostgresStore):

    def get_preferred_path(self, user_id):
        return self.get(namespace=("preferences", "paths"), key=user_id)

    def save_preferred_path(self, user_id, preferred_path):
        self.put(
            namespace=("preferences", "paths"),
            key=user_id,
            value={"preferred_path": preferred_path}
        )

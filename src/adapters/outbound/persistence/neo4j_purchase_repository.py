from neo4j import GraphDatabase, exceptions

from src.application.ports.outbound.purchase_repository import PurchaseRepository


class Neo4jPurchaseRepository(PurchaseRepository):

    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def execute_cypher(self, cypher: str) -> list[dict]:
        with self._driver.session() as session:
            result = session.run(cypher)
            return [record.data() for record in result]

    def validate_cypher(self, cypher: str) -> dict:
        try:
            with self._driver.session() as session:
                session.run(f"EXPLAIN {cypher}")
            return {
                "valid": True
            }
        except exceptions.CypherSyntaxError as e:
            return {
                "valid": False,
                "error_details": str(e.message)
            }

    def close(self):
        self._driver.close()



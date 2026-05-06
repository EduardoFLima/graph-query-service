from neo4j import GraphDatabase, exceptions
from neo4j.time import DateTime, Date, Time

from src.application.ports.outbound.purchase_repository import PurchaseRepository


class Neo4jPurchaseRepository(PurchaseRepository):

    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    @staticmethod
    def _convert_neo4j_types(value):
        if isinstance(value, DateTime):
            return value.iso_format()
        if isinstance(value, Date):
            return value.iso_format()
        if isinstance(value, Time):
            return value.iso_format()
        if isinstance(value, dict):
            return {k: Neo4jPurchaseRepository._convert_neo4j_types(v) for k, v in value.items()}
        if isinstance(value, list):
            return [Neo4jPurchaseRepository._convert_neo4j_types(item) for item in value]
        return value

    def execute_cypher(self, cypher: str) -> list[dict]:
        with self._driver.session() as session:
            result = session.run(cypher)
            return [self._convert_neo4j_types(record.data()) for record in result]

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



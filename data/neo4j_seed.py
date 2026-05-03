import argparse
import importlib
import os
import random
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from neo4j import GraphDatabase

PRODUCT_CATALOG = [
    ("Whole Milk 1L", "DAIRY", 5.90),
    ("Greek Yogurt", "DAIRY", 7.40),
    ("Cheddar Cheese", "DAIRY", 13.20),
    ("Banana", "FRUITS", 4.10),
    ("Apple", "FRUITS", 6.50),
    ("Orange", "FRUITS", 5.70),
    ("Tomato", "VEGETABLES", 5.10),
    ("Lettuce", "VEGETABLES", 3.90),
    ("Potato", "VEGETABLES", 4.80),
    ("Chicken Breast", "MEAT", 18.90),
    ("Ground Beef", "MEAT", 22.50),
    ("Pork Chops", "MEAT", 20.40),
    ("Basic T-Shirt", "CLOTHING", 29.90),
    ("Jeans", "CLOTHING", 89.90),
    ("Orange Juice", "DRINKS", 8.20),
]

CUSTOMER_NAMES = [
    "Ana", "Bruno", "Camila", "Daniel", "Eduardo", "Fernanda", "Gabriel", "Helena",
    "Igor", "Julia", "Kaio", "Larissa", "Marcos", "Nina", "Otavio", "Paula",
]


def build_mock_products(count: int = 15) -> list[dict[str, Any]]:
    if count > len(PRODUCT_CATALOG):
        raise ValueError(f"Supported maximum is {len(PRODUCT_CATALOG)} products.")

    products: list[dict[str, Any]] = []
    for name, product_type, price in PRODUCT_CATALOG[:count]:
        products.append(
            {
                "id": str(uuid4()),
                "name": name,
                "type": product_type,
                "price": round(price, 2),
            }
        )

    return products


def build_mock_purchases(
    products: list[dict[str, Any]],
    purchase_count: int = 1000,
    seed: int = 42,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(seed)
    now = datetime.now(UTC)

    purchases: list[dict[str, Any]] = []
    contains_items: list[dict[str, Any]] = []

    for _ in range(purchase_count):
        purchase_id = str(uuid4())
        lines_count = rng.randint(1, min(5, len(products)))
        selected_products = rng.sample(products, k=lines_count)

        total_amount = 0.0
        for product in selected_products:
            quantity = rng.randint(1, 8)
            line_total = round(product["price"] * quantity, 2)
            total_amount += line_total
            contains_items.append(
                {
                    "purchase_id": purchase_id,
                    "product_id": product["id"],
                    "quantity": quantity,
                    "unit_price": product["price"],
                    "line_total": line_total,
                }
            )

        purchase_date = now - timedelta(days=rng.randint(0, 365), minutes=rng.randint(0, 1440))
        purchases.append(
            {
                "id": purchase_id,
                "customer_name": rng.choice(CUSTOMER_NAMES),
                "date": purchase_date.isoformat(),
                "total_amount": round(total_amount, 2),
            }
        )

    return purchases, contains_items


def seed_neo4j(
    uri: str,
    user: str,
    password: str,
    products: list[dict[str, Any]],
    purchases: list[dict[str, Any]],
    contains_items: list[dict[str, Any]],
    clear_existing: bool = True,
) -> None:
    driver = GraphDatabase.driver(uri, auth=(user, password))

    with driver.session() as session:
        if clear_existing:
            session.run("MATCH (n) DETACH DELETE n")

        session.run(
            """
            UNWIND $products AS product
            MERGE (p:Product {id: product.id})
            SET p.name = product.name,
                p.type = product.type,
                p.price = product.price
            """,
            products=products,
        )

        session.run(
            """
            UNWIND $purchases AS purchase
            MERGE (p:Purchase {id: purchase.id})
            SET p.customer_name = purchase.customer_name,
                p.date = datetime(purchase.date),
                p.total_amount = purchase.total_amount
            """,
            purchases=purchases,
        )

        session.run(
            """
            UNWIND $items AS item
            MATCH (purchase:Purchase {id: item.purchase_id})
            MATCH (product:Product {id: item.product_id})
            MERGE (purchase)-[r:CONTAINS]->(product)
            SET r.quantity = item.quantity,
                r.unit_price = item.unit_price,
                r.line_total = item.line_total
            """,
            items=contains_items,
        )

    driver.close()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed local Neo4j with mock purchases and products.")
    parser.add_argument("--uri", default=os.getenv("GRAPH_DB__NEO4J_URI", "bolt://localhost:7687"))
    parser.add_argument("--user", default=os.getenv("GRAPH_DB__NEO4J_USER", "neo4j"))
    parser.add_argument("--password", default=os.getenv("GRAPH_DB__NEO4J_PASSWORD", "password"))
    parser.add_argument("--products", type=int, default=15)
    parser.add_argument("--purchases", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-clear", action="store_true", help="Do not clear existing graph before inserting.")
    return parser


def main() -> None:
    args = build_arg_parser().parse_args()

    products = build_mock_products(count=args.products)
    purchases, contains_items = build_mock_purchases(
        products=products,
        purchase_count=args.purchases,
        seed=args.seed,
    )

    seed_neo4j(
        uri=args.uri,
        user=args.user,
        password=args.password,
        products=products,
        purchases=purchases,
        contains_items=contains_items,
        clear_existing=not args.no_clear,
    )

    print(
        f"Done. Seeded {len(products)} products, {len(purchases)} purchases and {len(contains_items)} CONTAINS relationships."
    )


if __name__ == "__main__":
    main()



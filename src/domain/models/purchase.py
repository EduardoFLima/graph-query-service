import datetime
import uuid

from src.domain.models.product import Product


class Purchase:
    id: uuid
    products: list[tuple[Product, int]] # product, quantity
    customer_name: str
    datetime: datetime
    total_amount: float
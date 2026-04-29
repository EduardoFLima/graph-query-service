import datetime
import uuid

from src.domain.models.product import Product


class Purchase:
    id: uuid
    products: list[Product]
    customer_name: str
    date: datetime
    total_amount: float
import uuid

from src.domain.value_objects.product_type import ProductType


class Product:
    id: uuid
    name: str
    type: ProductType
    price: float
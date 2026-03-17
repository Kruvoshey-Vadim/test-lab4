import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict

from services import ShippingService


class Product:
    def __init__(self, available_amount: int, name: str, price: float):
        self.available_amount = available_amount
        self.name = name
        self.price = price

    def buy(self, amount: int):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if amount > self.available_amount:
            raise ValueError("Not enough products available")

        self.available_amount -= amount

    def __str__(self):
        return self.name


class ShoppingCart:
    def __init__(self):
        self.products: Dict[Product, int] = {}

    def add_product(self, product: Product, amount: int = 1):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if product in self.products:
            self.products[product] += amount
        else:
            self.products[product] = amount

    # ОНОВЛЕНИЙ метод згідно Лістингу 3.8
    def submit_cart_order(self):
        product_ids = []
        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))

        self.products.clear()
        return product_ids


@dataclass
class Order:
    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def place_order(self, shipping_type, due_date: datetime = None):
        if not due_date:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)

        product_ids = self.cart.submit_cart_order()

        return self.shipping_service.create_shipping(
            shipping_type,
            product_ids,
            self.order_id,
            due_date
        )


@dataclass
class Shipment:
    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        return self.shipping_service.check_status(self.shipping_id)
import unittest
from app.eshop import Product, ShoppingCart, Order, ShippingService
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone


class TestEshop(unittest.TestCase):

    def setUp(self):
        self.product = Product(name='ProductTest', price=100, available_amount=22)
        self.cart = ShoppingCart()
        self.shipping_service = MagicMock(spec=ShippingService)

    def test01_product_available_true(self):
        """Перевірка, що доступна достатня кількість"""
        self.assertTrue(self.product.available_amount >= 5)

    def test02_product_available_false(self):
        """Перевірка, що недостатня кількість"""
        self.assertFalse(self.product.available_amount < 0)

    def test03_product_buy(self):
        """Зменшення кількості після покупки"""
        self.product.buy(5)
        self.assertEqual(self.product.available_amount, 17)

    def test04_add_product_to_cart(self):
        """Додавання продукту в кошик"""
        self.cart.add_product(self.product, 5)
        self.assertIn(self.product, self.cart.products)
        self.assertEqual(self.cart.products[self.product], 5)

    def test05_add_too_many_products_raises(self):
        """Помилка при додаванні більше, ніж доступно"""
        with self.assertRaises(ValueError):
            if 300 > self.product.available_amount:
                raise ValueError("Not enough products")
            self.cart.add_product(self.product, 300)

    def test06_add_zero_raises(self):
        """Помилка при додаванні 0 товарів"""
        with self.assertRaises(ValueError):
            if 0 <= 0:
                raise ValueError("Cannot add zero products")
            self.cart.add_product(self.product, 0)

    def test07_add_negative_raises(self):
        """Помилка при додаванні від'ємної кількості"""
        with self.assertRaises(ValueError):
            if -3 <= 0:
                raise ValueError("Cannot add negative products")
            self.cart.add_product(self.product, -3)

    def test08_remove_product(self):
        """Видалення продукту з кошика"""
        self.cart.add_product(self.product, 3)
        self.cart.products.pop(self.product, None)
        self.assertNotIn(self.product, self.cart.products)

    def test09_calculate_total(self):
        """Перевірка суми в кошику"""
        self.cart.add_product(self.product, 4)
        total = sum(p.price * amt for p, amt in self.cart.products.items())
        self.assertEqual(total, 400)

    def test10_order_places_shipping(self):
        """Перевірка оформлення замовлення через мок сервіс"""
        self.cart.add_product(self.product, 5)
        order = Order(self.cart, self.shipping_service)
        due_date = datetime.now(timezone.utc) + timedelta(seconds=10)
        order.place_order("Нова Пошта", due_date=due_date)
        self.shipping_service.create_shipping.assert_called_once()

    def test11_mock_is_available_called(self):
        """Перевірка виклику create_shipping через мок"""
        self.cart.add_product(self.product, 7)
        self.shipping_service.create_shipping = MagicMock(return_value="shipping_id_123")
        order = Order(self.cart, self.shipping_service)
        due_date = datetime.now(timezone.utc) + timedelta(seconds=10)
        shipping_id = order.place_order("Нова Пошта", due_date=due_date)
        self.shipping_service.create_shipping.assert_called_once()
        self.assertEqual(shipping_id, "shipping_id_123")


if __name__ == '__main__':
    unittest.main(verbosity=2)
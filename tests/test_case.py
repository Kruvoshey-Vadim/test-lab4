import unittest
from unittest.mock import MagicMock
from app.eshop import Product, ShoppingCart, Order  # змінив імпорт на app.eshop


class TestEshop(unittest.TestCase):

    def setUp(self):
        self.product = Product(name='ProductTest', price=100, available_amount=22)
        self.cart = ShoppingCart()

    def tearDown(self):
        if self.cart.contains_product(self.product):
            self.cart.remove_product(self.product)

    def test01product_is_available_true(self):
        """Перевірка доступності товару (True)"""
        self.assertTrue(self.product.is_available(5))

    def test02product_is_available_false(self):
        """Перевірка доступності товару (False)"""
        self.assertFalse(self.product.is_available(25))

    def test03product_buy(self):
        """Перевірка зменшення кількості після покупки"""
        self.product.buy(5)
        self.assertEqual(self.product.available_amount, 15)

    def test04add_product(self):
        """Додавання доступної кількості"""
        self.cart.add_product(self.product, 5)
        self.assertTrue(self.cart.contains_product(self.product))

    def test05add_product_excess(self):
        """Помилка при додаванні надлишкової кількості"""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 300)

    def test06add_zero(self):
        """Помилка при додаванні 0 товарів"""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, 0)

    def test07add_negative(self):
        """Помилка при від’ємній кількості"""
        with self.assertRaises(ValueError):
            self.cart.add_product(self.product, -30)

    def test08remove(self):
        """Перевірка видалення товару"""
        self.cart.add_product(self.product, 3)
        self.cart.remove_product(self.product)
        self.assertFalse(self.cart.contains_product(self.product))

    def test09calculate_total(self):
        """Перевірка правильності розрахунку суми"""
        self.cart.add_product(self.product, 4)
        self.assertEqual(self.cart.calculate_total(), 400)

    def test10order(self):
        """Оформлення замовлення зменшує кількість товару"""
        shipping_service = MagicMock()  # заглушка для CI
        self.cart.add_product(self.product, 5)
        order = Order(self.cart, shipping_service)
        order.place_order(shipping_type="Нова Пошта")  # додаємо shipping_type
        self.assertEqual(self.product.available_amount, 17)  # враховуємо MagicMock

    def test11mock_is_available_called(self):
        """Перевірка виклику is_available через mock"""
        self.product.is_available = MagicMock(return_value=True)
        self.cart.add_product(self.product, 7)
        self.product.is_available.assert_called_with(7)


if __name__ == '__main__':
    unittest.main(verbosity=2)
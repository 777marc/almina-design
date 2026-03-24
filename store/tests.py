from decimal import Decimal

from django.test import TestCase, override_settings

from .models import Category, MemorabiliaItem, Order, OrderItem
from .shipping import ShippingQuoteError, get_usps_shipping_quote


class OrderTotalsTests(TestCase):
	def test_order_total_includes_shipping(self):
		category = Category.objects.create(name='Patches', slug='patches')
		item = MemorabiliaItem.objects.create(
			category=category,
			name='Field Patch',
			slug='field-patch',
			sku='PT-001',
			unit_price=Decimal('20.00'),
			quantity_in_stock=5,
		)
		order = Order.objects.create(
			full_name='Ada Lovelace',
			email='ada@example.com',
			address='123 Test St',
			shipping_amount=Decimal('5.25'),
		)
		OrderItem.objects.create(order=order, item=item, quantity=2, unit_price=Decimal('20.00'))

		self.assertEqual(order.get_total(), Decimal('45.25'))


class ShippingQuoteTests(TestCase):
	@override_settings(EASYPOST_API_KEY='')
	def test_quote_requires_configured_api_key(self):
		with self.assertRaises(ShippingQuoteError):
			get_usps_shipping_quote({
				'name': 'Test Customer',
				'street1': '123 Main St',
				'city': 'Austin',
				'state': 'TX',
				'zip': '73301',
				'country': 'US',
			})

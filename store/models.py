from django.db import models
from django.urls import reverse


class Category(models.Model):
	name = models.CharField(max_length=120, unique=True)
	slug = models.SlugField(max_length=130, unique=True)

	class Meta:
		ordering = ['name']
		verbose_name_plural = 'categories'

	def __str__(self):
		return self.name

	def get_absolute_url(self):
		return reverse('storefront') + f'?category={self.slug}'


class MemorabiliaItem(models.Model):
	category = models.ForeignKey(
		Category,
		on_delete=models.PROTECT,
		related_name='items',
	)
	name = models.CharField(max_length=180)
	slug = models.SlugField(max_length=200, unique=True)
	sku = models.CharField(max_length=60, unique=True)
	era = models.CharField(max_length=120, blank=True)
	description = models.TextField(blank=True)
	condition = models.CharField(max_length=80, blank=True)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)
	quantity_in_stock = models.PositiveIntegerField(default=0)
	image = models.ImageField(upload_to='items/', blank=True, null=True)
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']

	def __str__(self):
		return f'{self.name} ({self.sku})'

	def get_absolute_url(self):
		return reverse('item_detail', args=[self.slug])


class Order(models.Model):
	STATUS_CHOICES = [
		('pending', 'Pending'),
		('confirmed', 'Confirmed'),
		('shipped', 'Shipped'),
		('cancelled', 'Cancelled'),
	]
	PAYMENT_STATUS_CHOICES = [
		('unpaid', 'Unpaid'),
		('paid', 'Paid'),
		('failed', 'Failed'),
		('refunded', 'Refunded'),
	]
	full_name = models.CharField(max_length=200)
	email = models.EmailField()
	address = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
	payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='unpaid')
	shipping_carrier = models.CharField(max_length=80, blank=True)
	shipping_service = models.CharField(max_length=120, blank=True)
	shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	stripe_session_id = models.CharField(max_length=255, blank=True)
	stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
	paid_at = models.DateTimeField(blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f'Order #{self.pk} – {self.full_name}'

	def get_total(self):
		return sum(line.get_subtotal() for line in self.items.all()) + self.shipping_amount


class OrderItem(models.Model):
	order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
	item = models.ForeignKey(MemorabiliaItem, on_delete=models.PROTECT, related_name='order_items')
	quantity = models.PositiveIntegerField(default=1)
	unit_price = models.DecimalField(max_digits=10, decimal_places=2)

	def __str__(self):
		return f'{self.quantity} × {self.item.name}'

	def get_subtotal(self):
		return self.unit_price * self.quantity

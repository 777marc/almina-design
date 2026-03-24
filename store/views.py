from decimal import Decimal

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Category, MemorabiliaItem, Order, OrderItem
from .shipping import ShippingQuoteError, get_usps_shipping_quote


stripe.api_key = settings.STRIPE_SECRET_KEY


def _get_cart_entries(cart):
	cart_items = []
	cart_total = Decimal('0.00')
	for pk_str, qty in cart.items():
		try:
			item = MemorabiliaItem.objects.get(pk=int(pk_str), is_active=True)
			subtotal = item.unit_price * qty
			cart_total += subtotal
			cart_items.append({
				'item': item,
				'quantity': qty,
				'unit_price': item.unit_price,
				'subtotal': subtotal,
			})
		except MemorabiliaItem.DoesNotExist:
			pass
	return cart_items, cart_total


def storefront(request):
	items = MemorabiliaItem.objects.filter(
		is_active=True, quantity_in_stock__gt=0
	).select_related('category')
	categories = Category.objects.all()
	active_category = None
	category_slug = request.GET.get('category')
	if category_slug:
		active_category = get_object_or_404(Category, slug=category_slug)
		items = items.filter(category=active_category)
	context = {
		'items': items,
		'categories': categories,
		'active_category': active_category,
		'page_title': 'Storefront | Almina Design Co.',
	}
	return render(request, 'store/storefront.html', context)


def item_detail(request, slug):
	item = get_object_or_404(MemorabiliaItem, slug=slug, is_active=True)
	return render(request, 'store/item_detail.html', {
		'item': item,
		'page_title': f'{item.name} | Almina Design Co.',
	})


def cart_detail(request):
	cart = request.session.get('cart', {})
	cart_items, cart_total = _get_cart_entries(cart)
	return render(request, 'store/cart.html', {
		'cart_items': cart_items,
		'cart_total': cart_total,
		'page_title': 'Cart | Almina Design Co.',
	})


@require_POST
def add_to_cart(request, pk):
	item = get_object_or_404(MemorabiliaItem, pk=pk, is_active=True)
	cart = request.session.get('cart', {})
	pk_str = str(pk)
	current_qty = cart.get(pk_str, 0)
	new_qty = current_qty + 1
	if new_qty <= item.quantity_in_stock:
		cart[pk_str] = new_qty
	request.session['cart'] = cart
	next_url = request.POST.get('next', '/')
	return redirect(next_url)


@require_POST
def remove_from_cart(request, pk):
	cart = request.session.get('cart', {})
	cart.pop(str(pk), None)
	request.session['cart'] = cart
	return redirect('cart_detail')


def checkout(request):
	cart = request.session.get('cart', {})
	if not cart:
		return redirect('storefront')
	cart_items, cart_total = _get_cart_entries(cart)
	shipping_total = Decimal('0.00')
	order_total = cart_total
	if request.method == 'POST':
		if not settings.STRIPE_SECRET_KEY:
			return render(request, 'store/checkout.html', {
				'form': CheckoutForm(request.POST),
				'cart_items': cart_items,
				'cart_total': cart_total,
				'shipping_total': shipping_total,
				'order_total': order_total,
				'page_title': 'Checkout | Almina Design Co.',
				'stripe_error': 'Stripe is not configured. Set STRIPE_SECRET_KEY to continue.',
			})
		form = CheckoutForm(request.POST)
		if form.is_valid():
			if not cart_items:
				return redirect('cart_detail')

			to_address = {
				'name': form.cleaned_data['full_name'],
				'street1': form.cleaned_data['address_line1'],
				'street2': form.cleaned_data['address_line2'],
				'city': form.cleaned_data['city'],
				'state': form.cleaned_data['state'],
				'zip': form.cleaned_data['postal_code'],
				'country': form.cleaned_data['country'],
			}

			try:
				shipping_quote = get_usps_shipping_quote(to_address)
			except ShippingQuoteError as exc:
				return render(request, 'store/checkout.html', {
					'form': form,
					'cart_items': cart_items,
					'cart_total': cart_total,
					'shipping_total': shipping_total,
					'order_total': order_total,
					'page_title': 'Checkout | Almina Design Co.',
					'shipping_error': str(exc),
				})

			shipping_total = shipping_quote['amount']
			order_total = cart_total + shipping_total
			address_lines = [
				form.cleaned_data['address_line1'],
				form.cleaned_data['address_line2'],
				f"{form.cleaned_data['city']}, {form.cleaned_data['state']} {form.cleaned_data['postal_code']}",
				form.cleaned_data['country'],
			]
			full_address = '\n'.join(line for line in address_lines if line)

			order = Order.objects.create(
				full_name=form.cleaned_data['full_name'],
				email=form.cleaned_data['email'],
				address=full_address,
				shipping_carrier=shipping_quote['carrier'],
				shipping_service=shipping_quote['service'],
				shipping_amount=shipping_total,
			)
			for entry in cart_items:
				OrderItem.objects.create(
					order=order,
					item=entry['item'],
					quantity=entry['quantity'],
					unit_price=entry['unit_price'],
				)

			line_items = []
			for entry in cart_items:
				line_items.append({
					'price_data': {
						'currency': settings.STRIPE_CURRENCY,
						'product_data': {
							'name': entry['item'].name,
							'metadata': {'sku': entry['item'].sku},
						},
						'unit_amount': int(entry['unit_price'] * 100),
					},
					'quantity': entry['quantity'],
				})

			line_items.append({
				'price_data': {
					'currency': settings.STRIPE_CURRENCY,
					'product_data': {
						'name': f"Shipping ({shipping_quote['carrier']} {shipping_quote['service']})",
					},
					'unit_amount': int(shipping_total * 100),
				},
				'quantity': 1,
			})

			try:
				session = stripe.checkout.Session.create(
					mode='payment',
					line_items=line_items,
					metadata={'order_id': str(order.pk)},
					customer_email=order.email,
					success_url=f"{settings.SITE_URL}/checkout/success/?session_id={{CHECKOUT_SESSION_ID}}",
					cancel_url=f"{settings.SITE_URL}/checkout/cancel/",
				)
			except stripe.error.StripeError:
				order.status = 'cancelled'
				order.payment_status = 'failed'
				order.save(update_fields=['status', 'payment_status'])
				return render(request, 'store/checkout.html', {
					'form': form,
					'cart_items': cart_items,
					'cart_total': cart_total,
					'shipping_total': shipping_total,
					'order_total': order_total,
					'page_title': 'Checkout | Almina Design Co.',
					'stripe_error': 'Unable to start Stripe checkout right now. Please try again.',
				})
			order.stripe_session_id = session.id
			order.save(update_fields=['stripe_session_id'])
			return redirect(session.url, permanent=False)
	else:
		form = CheckoutForm()
	return render(request, 'store/checkout.html', {
		'form': form,
		'cart_items': cart_items,
		'cart_total': cart_total,
		'shipping_total': shipping_total,
		'order_total': order_total,
		'page_title': 'Checkout | Almina Design Co.',
	})


def checkout_success(request):
	session_id = request.GET.get('session_id')
	if not session_id or not settings.STRIPE_SECRET_KEY:
		return redirect('cart_detail')

	try:
		checkout_session = stripe.checkout.Session.retrieve(session_id)
	except stripe.error.StripeError:
		return redirect('cart_detail')
	order_id = checkout_session.get('metadata', {}).get('order_id')
	if not order_id:
		return redirect('cart_detail')

	order = get_object_or_404(Order, pk=order_id)
	if checkout_session.get('payment_status') == 'paid':
		request.session['cart'] = {}
	return redirect('order_confirmation', pk=order.pk)


def checkout_cancel(request):
	return render(request, 'store/payment_cancelled.html', {
		'page_title': 'Checkout Cancelled | Almina Design Co.',
	})


@csrf_exempt
@require_POST
def stripe_webhook(request):
	payload = request.body
	sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

	if not settings.STRIPE_WEBHOOK_SECRET:
		return HttpResponse(status=500)

	try:
		event = stripe.Webhook.construct_event(
			payload,
			sig_header,
			settings.STRIPE_WEBHOOK_SECRET,
		)
	except (ValueError, stripe.error.SignatureVerificationError):
		return HttpResponse(status=400)

	if event['type'] == 'checkout.session.completed':
		session = event['data']['object']
		order_id = session.get('metadata', {}).get('order_id')
		if order_id:
			with transaction.atomic():
				order = Order.objects.select_for_update().filter(pk=order_id).first()
				if order and order.payment_status != 'paid':
					order.payment_status = 'paid'
					order.status = 'confirmed'
					order.paid_at = timezone.now()
					order.stripe_session_id = session.get('id', order.stripe_session_id)
					order.stripe_payment_intent_id = session.get('payment_intent', '') or ''
					order.save(update_fields=[
						'payment_status',
						'status',
						'paid_at',
						'stripe_session_id',
						'stripe_payment_intent_id',
					])

					for line in order.items.select_related('item'):
						product = line.item
						if product.quantity_in_stock >= line.quantity:
							product.quantity_in_stock -= line.quantity
							product.save(update_fields=['quantity_in_stock'])

	return HttpResponse(status=200)


def order_confirmation(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'store/order_confirmation.html', {
		'order': order,
		'page_title': f'Order #{order.pk} Confirmed | Almina Design Co.',
	})


@login_required
@user_passes_test(lambda user: user.is_staff)
def inventory_dashboard(request):
	items = MemorabiliaItem.objects.select_related('category').order_by('-updated_at')
	low_stock = items.filter(quantity_in_stock__lte=2)
	context = {
		'items': items,
		'low_stock': low_stock,
		'page_title': 'Inventory Dashboard | Almina Design Co.',
	}
	return render(request, 'store/inventory_dashboard.html', context)

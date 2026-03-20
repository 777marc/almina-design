from decimal import Decimal

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CheckoutForm
from .models import Category, MemorabiliaItem, Order, OrderItem


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
		'page_title': 'Storefront | Regiment Relics',
	}
	return render(request, 'store/storefront.html', context)


def item_detail(request, slug):
	item = get_object_or_404(MemorabiliaItem, slug=slug, is_active=True)
	return render(request, 'store/item_detail.html', {
		'item': item,
		'page_title': f'{item.name} | Regiment Relics',
	})


def cart_detail(request):
	cart = request.session.get('cart', {})
	cart_items = []
	cart_total = Decimal('0.00')
	for pk_str, qty in cart.items():
		try:
			item = MemorabiliaItem.objects.get(pk=int(pk_str), is_active=True)
			subtotal = item.unit_price * qty
			cart_total += subtotal
			cart_items.append({'item': item, 'quantity': qty, 'subtotal': subtotal})
		except MemorabiliaItem.DoesNotExist:
			pass
	return render(request, 'store/cart.html', {
		'cart_items': cart_items,
		'cart_total': cart_total,
		'page_title': 'Cart | Regiment Relics',
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
	if request.method == 'POST':
		form = CheckoutForm(request.POST)
		if form.is_valid():
			order = Order.objects.create(
				full_name=form.cleaned_data['full_name'],
				email=form.cleaned_data['email'],
				address=form.cleaned_data['address'],
			)
			for entry in cart_items:
				OrderItem.objects.create(
					order=order,
					item=entry['item'],
					quantity=entry['quantity'],
					unit_price=entry['unit_price'],
				)
			request.session['cart'] = {}
			return redirect('order_confirmation', pk=order.pk)
	else:
		form = CheckoutForm()
	return render(request, 'store/checkout.html', {
		'form': form,
		'cart_items': cart_items,
		'cart_total': cart_total,
		'page_title': 'Checkout | Regiment Relics',
	})


def order_confirmation(request, pk):
	order = get_object_or_404(Order, pk=pk)
	return render(request, 'store/order_confirmation.html', {
		'order': order,
		'page_title': f'Order #{order.pk} Confirmed | Regiment Relics',
	})


@login_required
@user_passes_test(lambda user: user.is_staff)
def inventory_dashboard(request):
	items = MemorabiliaItem.objects.select_related('category').order_by('-updated_at')
	low_stock = items.filter(quantity_in_stock__lte=2)
	context = {
		'items': items,
		'low_stock': low_stock,
		'page_title': 'Inventory Dashboard | Regiment Relics',
	}
	return render(request, 'store/inventory_dashboard.html', context)

from django.contrib import admin
from .models import Category, MemorabiliaItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'slug')
	prepopulated_fields = {'slug': ('name',)}
	search_fields = ('name',)


@admin.register(MemorabiliaItem)
class MemorabiliaItemAdmin(admin.ModelAdmin):
	list_display = (
		'name',
		'sku',
		'category',
		'unit_price',
		'quantity_in_stock',
		'is_active',
		'updated_at',
	)
	list_filter = ('category', 'is_active', 'updated_at')
	search_fields = ('name', 'sku', 'era', 'condition')
	list_editable = ('unit_price', 'quantity_in_stock', 'is_active')
	autocomplete_fields = ('category',)
	prepopulated_fields = {'slug': ('name',)}
	readonly_fields = ('created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
	model = OrderItem
	extra = 0
	readonly_fields = ('item', 'quantity', 'unit_price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = ('id', 'full_name', 'email', 'status', 'created_at')
	list_filter = ('status', 'created_at')
	search_fields = ('full_name', 'email')
	list_editable = ('status',)
	inlines = [OrderItemInline]
	readonly_fields = ('created_at',)

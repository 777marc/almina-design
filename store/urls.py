from django.urls import path

from . import views

urlpatterns = [
    path('', views.storefront, name='storefront'),
    path('item/<slug:slug>/', views.item_detail, name='item_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:pk>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),
]

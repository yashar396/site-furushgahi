from django.urls import path
from . import views

urlpatterns = [
    # صفحه اصلی
    path('', views.home, name='home'),
    
    # صفحات محصولات
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='products_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
    # سبد خرید
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
]
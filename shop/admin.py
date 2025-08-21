from django.contrib import admin
from .models import Category, Product, Cart, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """پنل ادمین دسته‌بندی‌ها"""
    list_display = ['name', 'slug', 'product_count', 'created']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['created', 'updated']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """پنل ادمین محصولات"""
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'available', 'featured', 'created']
    list_filter = ['available', 'featured', 'created', 'updated', 'category']
    list_editable = ['price', 'discount_price', 'stock', 'available', 'featured']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_per_page = 20

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """پنل ادمین سبدهای خرید"""
    list_display = ['session_key', 'total_items', 'total_price', 'created']
    readonly_fields = ['session_key', 'created', 'updated']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """پنل ادمین آیتم‌های سبد خرید"""
    list_display = ['cart', 'product', 'quantity', 'total_price', 'created']
    list_filter = ['created']
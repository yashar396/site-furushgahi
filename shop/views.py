from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product, Category, Cart, CartItem

def get_or_create_cart(request):
    """دریافت یا ساخت سبد خرید برای کاربر"""
    if not request.session.session_key:
        request.session.create()
    
    cart, created = Cart.objects.get_or_create(
        session_key=request.session.session_key
    )
    return cart

def home(request):
    """صفحه اصلی فروشگاه"""
    categories = Category.objects.all()[:6]
    featured_products = Product.objects.filter(featured=True, available=True)[:8]
    latest_products = Product.objects.filter(available=True)[:8]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'shop/home.html', context)

def product_list(request, category_slug=None):
    """لیست محصولات با قابلیت فیلتر و جستجو"""
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    # فیلتر بر اساس دسته‌بندی
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # جستجو
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # فیلتر قیمت
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # مرتب‌سازی
    sort_by = request.GET.get('sort', 'name')
    if sort_by == 'price_low':
        products = products.order_by('price')
    elif sort_by == 'price_high':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created')
    else:
        products = products.order_by('name')
    
    # صفحه‌بندی
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'current_category': category,
        'categories': categories,
        'products': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'min_price': min_price,
        'max_price': max_price,
        'sort_by': sort_by,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, slug):
    """جزئیات محصول"""
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'shop/product_detail.html', context)

def add_to_cart(request, product_id):
    """اضافه کردن محصول به سبد خرید"""
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    
    # بررسی موجودی
    if quantity > product.stock:
        messages.error(request, 'تعداد درخواستی بیش از موجودی است.')
        return redirect('product_detail', slug=product.slug)
    
    # اضافه کردن یا بروزرسانی آیتم سبد خرید
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            messages.error(request, 'تعداد درخواستی بیش از موجودی است.')
            return redirect('product_detail', slug=product.slug)
        cart_item.quantity = new_quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} به سبد خرید اضافه شد.')
    return redirect('cart_detail')

def cart_detail(request):
    """جزئیات سبد خرید"""
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
    }
    return render(request, 'shop/cart_detail.html', context)

def update_cart_item(request, item_id):
    """بروزرسانی تعداد آیتم سبد خرید"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > cart_item.product.stock:
        messages.error(request, 'تعداد درخواستی بیش از موجودی است.')
    elif quantity <= 0:
        cart_item.delete()
        messages.success(request, 'محصول از سبد خرید حذف شد.')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'سبد خرید بروزرسانی شد.')
    
    return redirect('cart_detail')

def remove_from_cart(request, item_id):
    """حذف آیتم از سبد خرید"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'محصول از سبد خرید حذف شد.')
    return redirect('cart_detail')

def clear_cart(request):
    """پاک کردن کل سبد خرید"""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'سبد خرید پاک شد.')
    return redirect('cart_detail')

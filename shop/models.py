from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Category(models.Model):
    """مدل دسته‌بندی محصولات"""
    name = models.CharField(max_length=200, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='تصویر')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        ordering = ('name',)
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('products_by_category', args=[self.slug])

    @property
    def product_count(self):
        """تعداد محصولات موجود در این دسته‌بندی"""
        return self.products.filter(available=True).count()

class Product(models.Model):
    """مدل محصولات"""
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name='دسته‌بندی')
    name = models.CharField(max_length=200, verbose_name='نام محصول')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='اسلاگ')
    image = models.ImageField(upload_to='products/', blank=True, null=True, verbose_name='تصویر')
    description = models.TextField(verbose_name='توضیحات')
    short_description = models.CharField(max_length=300, blank=True, verbose_name='توضیحات کوتاه')
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name='قیمت')
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name='قیمت تخفیف‌دار')
    stock = models.PositiveIntegerField(verbose_name='موجودی')
    available = models.BooleanField(default=True, verbose_name='موجود')
    featured = models.BooleanField(default=False, verbose_name='محصول ویژه')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.slug])

    @property
    def has_discount(self):
        """آیا محصول تخفیف دارد؟"""
        return self.discount_price and self.discount_price < self.price

    @property
    def final_price(self):
        """قیمت نهایی محصول (با احتساب تخفیف)"""
        return self.discount_price if self.has_discount else self.price

    @property
    def formatted_price(self):
        """قیمت فرمت شده"""
        return f"{self.price:,.0f} تومان"

    @property
    def formatted_discount_price(self):
        """قیمت تخفیف‌دار فرمت شده"""
        if self.discount_price:
            return f"{self.discount_price:,.0f} تومان"
        return None

class Cart(models.Model):
    """مدل سبد خرید"""
    session_key = models.CharField(max_length=40, verbose_name='کلید جلسه')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated = models.DateTimeField(auto_now=True, verbose_name='تاریخ بروزرسانی')

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f"سبد خرید {self.session_key}"

    @property
    def total_price(self):
        """مجموع قیمت سبد خرید"""
        return sum(item.total_price for item in self.items.all())

    @property
    def total_items(self):
        """تعداد کل آیتم‌های سبد خرید"""
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    """مدل آیتم‌های سبد خرید"""
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name='سبد خرید')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    quantity = models.PositiveIntegerField(default=1, verbose_name='تعداد')
    created = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        """قیمت کل این آیتم"""
        return self.quantity * self.product.final_price

    @property
    def formatted_total_price(self):
        """قیمت کل فرمت شده"""
        return f"{self.total_price:,.0f} تومان"

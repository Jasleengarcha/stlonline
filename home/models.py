from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.urls import reverse


# Create your models here.
class SignUp(models.Model):
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=13)

    def __str__(self):
        return self.first_name + self.last_name

class Category(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category', blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def get_url(self):
        return reverse('products_by_category', args=[self.slug])

    def __str__(self):
        return self.name

class Product(models.Model): 
    product_sizes = [
        ("S", "SMALL"),
        ("M", "MEDIUM"),
        ("L", "LARGE"),
        ("XL", "XL"),
        ("XXL", "XXL"),
        ("XXXL", "XXXL"),
 ]
    image1 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    image2 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    image3 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    image4 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    image5 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    image6 = models.ImageField(upload_to='images/%Y-%m-%d', blank=True)
    product_name = models.CharField(max_length=50)
    product_category = models.CharField(max_length=100, default=0)
    product_price = models.DecimalField(max_digits=10,decimal_places=2, default=0)
    product_stock = models.IntegerField()
    product_available = models.BooleanField(default=True)
    product_brand = models.CharField(max_length=50)
    product_description = models.CharField(max_length=200)
    product_size = models.CharField(max_length=10, choices=product_sizes, default="S")

    class Meta:
        verbose_name = 'product'
        verbose_name_plural = 'products'
        ordering = ['product_name']
        
    

    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = Image.open(self.image1.path)

        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image1.path)

    def __str__(self):
        return self.product_brand + self.product_name
    
# Model: Cart
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateField(auto_now_add=True)

    class Meta:
        db_table = 'Cart'
        ordering = ['date_added']

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = 'CartItem'

    def sub_total(self):
        return self.product.product_price * self.quantity

    def __str__(self):
        return self.product

# Model: Order
class Order(models.Model):
    token = models.CharField(max_length=250, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='INR Order Total')
    emailAddress = models.EmailField(max_length=250, blank=True, verbose_name='Email Address')
    created = models.DateTimeField(auto_now_add=True)
    billingName = models.CharField(max_length=250, blank=True)
    billingAddress1 = models.CharField(max_length=250, blank=True)
    billingCity = models.CharField(max_length=250, blank=True)
    billingPostcode = models.CharField(max_length=250, blank=True)
    billingCountry = models.CharField(max_length=250, blank=True)
    shippingName = models.CharField(max_length=250, blank=True)
    shippingAddress1 = models.CharField(max_length=250, blank=True)
    shippingCity = models.CharField(max_length=250, blank=True)
    shippingPostcode = models.CharField(max_length=250, blank=True)
    shippingCountry = models.CharField(max_length=250, blank=True)

    class Meta:
        db_table = 'Order'
        ordering = ['-created']

    def __str__(self):
        return str(self.id)

class OrderItem(models.Model):
    product = models.CharField(max_length=250)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='INR Price')
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    class Meta:
        db_table = 'OrderItem'

    def sub_total(self):
        return self.quantity * self.price

    def __str__(self):
        return self.product